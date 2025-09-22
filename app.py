from flask import Flask, render_template, request, redirect, url_for
import os
from PIL import Image
import numpy as np
import tensorflow as tf

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True) 
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Load the pre-trained model
model_path = './models/Brain_Tumors_vgg_final.h5'
model = tf.keras.models.load_model(model_path)

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


@app.route('/upload', methods=['POST'])
def upload_image():
    if 'image' not in request.files:
        return redirect(url_for('home'))

    image = request.files['image']
    if image.filename == '':
        return redirect(url_for('home'))

    # Save the uploaded image to the upload folder
    image_path = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
    image.save(image_path)

    # Preprocess the image and make a prediction
    processed_image = preprocess_image(image_path)
    predictions = model.predict(processed_image)
    predicted_class = class_labels[np.argmax(predictions)]

    # Render the result on the webpage (only prediction is passed)
    return render_template('index.html', prediction=predicted_class)



@app.route('/about')
def about():
    return render_template('brain_tumor.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


if __name__ == "__main__":
    app.run(port=5001, debug=True)
