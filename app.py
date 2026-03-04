from flask import Flask, jsonify, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
import uuid
from PIL import Image
import numpy as np
import tensorflow as tf

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH


def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# Load the pre-trained model (graceful failure so server can start)
model_path = './models/Brain_Tumors_vgg_final.h5'
model = None
try:
    model = tf.keras.models.load_model(model_path)
except Exception:
    model = None

# Output keys for vision_predict (model output order: glioma, meningioma, no tumor, pituitary)
PROB_KEYS = ['glioma', 'meningioma', 'no_tumor', 'pituitary']


def vision_predict(image_path):
    """
    Run inference on an image. Returns { label: str, confidence: float, probs: dict }.
    probs keys: glioma, meningioma, no_tumor, pituitary.
    """
    processed = preprocess_image(image_path)
    preds = model.predict(processed, verbose=0)[0]
    probs = {k: float(v) for k, v in zip(PROB_KEYS, preds)}
    idx = int(np.argmax(preds))
    label = PROB_KEYS[idx]
    confidence = float(preds[idx])
    return {"label": label, "confidence": confidence, "probs": probs}


def qa_check_image(image_path):
    """
    Imaging QA: check image quality before inference.
    Returns { safe_to_infer: bool, quality_score: float, warnings: list[str] }.
    """
    warnings = []
    try:
        img = Image.open(image_path).convert('RGB')
    except Exception as e:
        return {
            "safe_to_infer": False,
            "quality_score": 0.0,
            "warnings": [f"Could not open image: {e}"],
        }
    w, h = img.size
    arr = np.array(img) / 255.0
    mean_val = float(np.mean(arr))
    std_val = float(np.std(arr))

    if min(w, h) < 150:
        warnings.append(f"Image too small: {w}x{h} (min 150 required)")
    if mean_val < 0.15:
        warnings.append("Image too dark")
    if mean_val > 0.90:
        warnings.append("Image too bright")
    if std_val < 0.05:
        warnings.append("Low contrast")

    safe_to_infer = min(w, h) >= 150
    quality_score = float(np.clip(std_val, 0.0, 1.0))

    return {
        "safe_to_infer": safe_to_infer,
        "quality_score": quality_score,
        "warnings": warnings,
    }


def generate_report(qa, vision):
    """
    Generate a report from QA and vision results.
    Returns { findings: str, impression: str, next_steps: list[str], limitations: str, urgency: str }.
    """
    limitations = "Educational demo only. Not medical advice."

    if not qa.get("safe_to_infer", True):
        return {
            "findings": "; ".join(qa.get("warnings", []) or ["Image quality insufficient for analysis."]),
            "impression": "Inconclusive due to image quality",
            "next_steps": ["Obtain higher quality image.", "Consult a healthcare provider for clinical evaluation."],
            "limitations": limitations,
            "urgency": "low",
        }

    label = vision.get("label", "unknown")
    confidence = vision.get("confidence", 0.0)

    if confidence < 0.60:
        return {
            "findings": f"Model prediction: {label} (confidence {confidence:.2f}). Quality score: {qa.get('quality_score', 0):.2f}.",
            "impression": "Uncertain classification",
            "next_steps": ["Consider repeat imaging or expert review.", "Consult a healthcare provider."],
            "limitations": limitations,
            "urgency": "medium",
        }

    label_display = label.replace("_", " ")
    impression = f"Predicted: {label_display}"
    urgency = "low" if label == "no_tumor" else "medium"
    next_steps = ["Consult a healthcare provider for clinical evaluation."]
    if label != "no_tumor":
        next_steps.insert(0, "Further imaging or specialist referral may be indicated.")

    return {
        "findings": f"Model prediction: {label_display} (confidence {confidence:.2f}). Quality score: {qa.get('quality_score', 0):.2f}.",
        "impression": impression,
        "next_steps": next_steps,
        "limitations": limitations,
        "urgency": urgency,
    }


def orchestrate(image_path):
    """
    Orchestrate QA, vision inference, and report generation.
    Returns { request_id, qa, vision, report, artifacts }.
    """
    request_id = str(uuid.uuid4())
    qa = qa_check_image(image_path)

    if not qa.get("safe_to_infer", False):
        vision = {}
        report = generate_report(qa, vision)
        return {
            "request_id": request_id,
            "qa": qa,
            "vision": vision,
            "report": report,
            "artifacts": {},
        }

    vision = vision_predict(image_path)
    report = generate_report(qa, vision)
    return {
        "request_id": request_id,
        "qa": qa,
        "vision": vision,
        "report": report,
        "artifacts": {},
    }


def preprocess_image(image_path):
    """
    Preprocess the uploaded image to make it compatible with the model.
    """
    img = Image.open(image_path).convert('RGB')  # Ensure 3 channels (RGB)
    img = img.resize((224, 224))  # Resize to the model's expected input size
    img_array = np.array(img) / 255.0  # Normalize pixel values to [0, 1]
    img_array = np.expand_dims(img_array, axis=0)  # Add batch dimension
    return img_array


@app.route('/healthz', methods=['GET'])
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


@app.route('/')
def home():
    return render_template('index.html')



# @app.route('/upload', methods=['POST'])
# def upload_image():
#     if 'image' not in request.files:
#         return redirect(url_for('home'))

#     image = request.files['image']
#     if image.filename == '':
#         return redirect(url_for('home'))

#     # Save the uploaded image to the upload folder
#     image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
#     image.save(image_path)

#     # Preprocess the image and make a prediction
#     processed_image = preprocess_image(image_path)
#     predictions = model.predict(processed_image)
#     predicted_class = class_labels[np.argmax(predictions)]

#     # Render the result on the webpage
#     return render_template(
#         'index.html', 
#         uploaded_image=url_for('static', filename=f'uploads/{image.filename}'),
#         prediction=predicted_class
#     )


@app.errorhandler(413)
def request_entity_too_large(error):
    """Handle file too large (exceeds MAX_CONTENT_LENGTH)."""
    return render_template('index.html', error='File too large. Maximum size is 5 MB.'), 413


@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return render_template('index.html', error='No file selected.')

    image = request.files['image']
    if image.filename == '':
        return render_template('index.html', error='No file selected.')

    if not allowed_file(image.filename):
        return render_template(
            'index.html',
            error='Invalid file type. Allowed formats: PNG, JPG, JPEG.'
        )

    filename = secure_filename(image.filename)
    if filename == '':
        return render_template('index.html', error='Invalid filename.')

    image_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(image_path)

    if model is None:
        return render_template(
            'index.html',
            error='Model not available. Please try again later.'
        )

    try:
        result = vision_predict(image_path)
        return render_template('index.html', prediction=result['label'])
    except Exception as e:
        return render_template(
            'index.html',
            error=f'Could not process image. Please ensure it is a valid PNG, JPG, or JPEG file. ({str(e)})'
        )



@app.route('/about')
def about():
    return render_template('brain_tumor.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == "__main__":
    app.run(port=5001, debug=True)
