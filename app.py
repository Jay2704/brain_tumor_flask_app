from flask import Flask, Response, jsonify, render_template, request, redirect, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
import gc
import logging
import os
import uuid
import tensorflow as tf

from agent.orchestrator import run as orchestrate

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Resolve project paths from this file location (stable across cwd differences).
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


def api_error(code: str, message: str, status: int = 400):
    """Return standardized API error response."""
    return jsonify({"error": {"code": code, "message": message}}), status


# Load the pre-trained model (graceful failure so server can start).
# Model path is absolute and rooted at BASE_DIR to avoid cwd-related failures.
model_path = os.path.join(BASE_DIR, "models", "Brain_Tumors_vgg_final.h5")
model = None
try:
    model = tf.keras.models.load_model(model_path)
except Exception as e:
    model = None
    logging.exception("Model load failed for %s: %s", model_path, e)
else:
    logging.info("Startup: TensorFlow model loaded from %s", model_path)

logging.info("Startup: model_loaded=%s", model is not None)
print(f"Startup check: model_loaded={model is not None} path={model_path}")

CLASS_LABELS = ["glioma", "meningioma", "no_tumor", "pituitary"]


@app.route("/healthz", methods=["GET"])
def healthz():
    # Use this endpoint for backend readiness checks in local/prod environments.
    """Health check for load balancers and uptime probes."""
    model_loaded = model is not None
    ok = model_loaded
    payload = {
        "ok": ok,
        "model_loaded": model_loaded,
        "service": "Medical MRI Diagnosis AI Agent API",
        "model_path": model_path,
    }
    status = 200 if ok else 500
    return jsonify(payload), status


@app.route("/")
def home():
    return render_template("index.html")


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large (exceeds MAX_CONTENT_LENGTH)."""
    if request.path.startswith("/api/"):
        return api_error("FILE_TOO_LARGE", "File too large. Maximum size is 5 MB.", 413)
    return render_template("index.html", error="File too large. Maximum size is 5 MB."), 413


@app.errorhandler(500)
def internal_server_error(error):
    """Ensure API routes always return JSON on 500."""
    if request.path.startswith("/api/"):
        msg = str(getattr(error, "description", None) or getattr(error, "message", str(error)))
        return api_error("INTERNAL_SERVER_ERROR", msg or "Internal server error", 500)
    return Response("Internal Server Error", status=500, mimetype="text/plain")


@app.route("/upload", methods=["POST"])
def upload_image():
    if "image" not in request.files:
        return render_template("index.html", error="No file selected.")

    image = request.files["image"]
    if image.filename == "":
        return render_template("index.html", error="No file selected.")

    if not allowed_file(image.filename):
        return render_template(
            "index.html",
            error="Invalid file type. Allowed formats: PNG, JPG, JPEG.",
        )

    filename = secure_filename(image.filename)
    if filename == "":
        return render_template("index.html", error="Invalid filename.")

    file_prefix = str(uuid.uuid4())
    safe_name = f"{file_prefix}_{filename}"
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
    image.save(image_path)

    if model is None:
        return render_template(
            "index.html",
            error="Analysis is temporarily unavailable. Please ensure the model file (Brain_Tumors_vgg_final.h5) is in the models/ folder and restart the application.",
        )

    try:
        uploaded_image_url = url_for("static", filename=f"uploads/{safe_name}")
        result = orchestrate(image_path, model, CLASS_LABELS, uploaded_image_url)
        qa = result["qa"]
        vision = result.get("vision") or {}
        prediction = vision.get("label", "Inconclusive")
        confidence = vision.get("confidence")
        warnings = qa.get("warnings", [])
        quality_score = qa.get("quality_score")
        return render_template(
            "index.html",
            prediction=prediction,
            confidence=confidence,
            warnings=warnings,
            quality_score=quality_score,
        )
    except Exception as e:
        return render_template(
            "index.html",
            error=f"Could not process image. Please ensure it is a valid PNG, JPG, or JPEG file. ({str(e)})",
        )
    finally:
        # Keep memory pressure low on constrained hosts after inference completes.
        gc.collect()


@app.route("/api/v1/analyze", methods=["POST"])
def api_v1_analyze():
    """Analyze uploaded MRI image. Returns standardized JSON."""
    try:
        if "image" not in request.files:
            return api_error("MISSING_FILE", "No file selected. Use multipart form field 'image'.", 400)

        image = request.files["image"]
        if image.filename == "":
            return api_error("EMPTY_FILENAME", "No file selected.", 400)

        if not allowed_file(image.filename):
            return api_error(
                "UNSUPPORTED_EXTENSION",
                "Invalid file type. Allowed: PNG, JPG, JPEG.",
                400,
            )

        filename = secure_filename(image.filename)
        if filename == "":
            return api_error("INVALID_FILENAME", "Invalid filename.", 400)

        if model is None:
            return api_error(
                "MODEL_UNAVAILABLE",
                "Model is not available on the server.",
                503,
            )

        file_prefix = str(uuid.uuid4())
        safe_name = f"{file_prefix}_{filename}"
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
        image.save(image_path)

        uploaded_image_url = url_for("static", filename=f"uploads/{safe_name}")
        result = orchestrate(image_path, model, CLASS_LABELS, uploaded_image_url)
        if not result["qa"].get("safe_to_infer", False):
            result["vision"] = None
        return jsonify(result), 200
    except Exception as e:
        logging.exception("Analysis failed: %s", e)
        return api_error(
            "INTERNAL_SERVER_ERROR",
            f"Analysis failed: {str(e)}",
            500,
        )
    finally:
        # Keep memory pressure low on constrained hosts after inference completes.
        gc.collect()


@app.route("/api/analyze", methods=["POST"])
def api_analyze():
    """Legacy analyze endpoint (redirects to same logic as v1)."""
    return api_v1_analyze()


@app.route("/about")
def about():
    return render_template("brain_tumor.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


if __name__ == "__main__":
    # Production entrypoint: gunicorn wsgi:app
    app.run(port=5001, debug=True)
