from flask import Flask, Response, jsonify, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import logging
import os
import uuid
import tensorflow as tf

from agent.orchestrator import run as orchestrate

app = Flask(__name__)

UPLOAD_FOLDER = "static/uploads"
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg"}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

CORS_ROUTES = {"/api/analyze", "/api/v1/analyze", "/healthz"}


@app.after_request
def add_cors_headers(response):
    """Add CORS headers for API routes (React dev server)."""
    if request.path in CORS_ROUTES:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    return response


@app.before_request
def handle_options_preflight():
    """Respond to OPTIONS preflight for CORS."""
    if request.method == "OPTIONS" and request.path in CORS_ROUTES:
        return Response("", status=204)


def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


# Load the pre-trained model (graceful failure so server can start)
model_path = "./models/Brain_Tumors_vgg_final.h5"
model = None
try:
    model = tf.keras.models.load_model(model_path)
except Exception as e:
    model = None
    logging.exception("Model load failed for %s: %s", model_path, e)

CLASS_LABELS = ["glioma", "meningioma", "no_tumor", "pituitary"]


@app.route("/healthz", methods=["GET"])
def healthz():
    """Health check endpoint. Returns 500 if model failed to load."""
    model_loaded = model is not None
    ok = model_loaded
    payload = {
        "ok": ok,
        "model_loaded": model_loaded,
        "model_path": os.path.abspath(model_path),
    }
    status = 200 if ok else 500
    return jsonify(payload), status


@app.route("/")
def home():
    return render_template("index.html")


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large (exceeds MAX_CONTENT_LENGTH)."""
    return render_template("index.html", error="File too large. Maximum size is 5 MB."), 413


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


@app.route("/api/v1/analyze", methods=["POST"])
def api_v1_analyze():
    """Analyze uploaded MRI image. Returns JSON with qa, vision, report."""
    if "image" not in request.files:
        return jsonify({"error": "No file selected."}), 400

    image = request.files["image"]
    if image.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not allowed_file(image.filename):
        return jsonify({"error": "Invalid file type. Allowed: PNG, JPG, JPEG."}), 400

    filename = secure_filename(image.filename)
    if filename == "":
        return jsonify({"error": "Invalid filename."}), 400

    file_prefix = str(uuid.uuid4())
    safe_name = f"{file_prefix}_{filename}"
    image_path = os.path.join(app.config["UPLOAD_FOLDER"], safe_name)
    image.save(image_path)

    if model is None:
        return jsonify({
            "error": "Model not available.",
            "detail": "The model file (Brain_Tumors_vgg_final.h5) was not found or failed to load. Please ensure it exists in the models/ folder and restart the application.",
        }), 503

    try:
        uploaded_image_url = url_for("static", filename=f"uploads/{safe_name}")
        result = orchestrate(image_path, model, CLASS_LABELS, uploaded_image_url)
        if not result["qa"].get("safe_to_infer", False):
            result["vision"] = None
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


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
    app.run(port=5001, debug=True)
