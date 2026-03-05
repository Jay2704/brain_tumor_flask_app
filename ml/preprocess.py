"""Image preprocessing for the brain tumor model."""
import numpy as np
from PIL import Image


def preprocess_image(image_path):
    """
    Preprocess the uploaded image to make it compatible with the model.
    """
    img = Image.open(image_path).convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img) / 255.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array
