from flask import Flask, jsonify, render_template, request, redirect, url_for
from werkzeug.utils import secure_filename
import os
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

# Class labels for predictions (modify based on your model)
class_labels = ['glioma', 'meningioma', 'no tumor', 'pituitary']


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
        processed_image = preprocess_image(image_path)
        predictions = model.predict(processed_image)
        predicted_class = class_labels[np.argmax(predictions)]
        return render_template('index.html', prediction=predicted_class)
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
