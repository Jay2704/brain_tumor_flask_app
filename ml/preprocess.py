"""Image preprocessing for the brain tumor model."""
import numpy as np
from PIL import Image


def preprocess_image(image_path):
    """
    Preprocess the uploaded image to make it compatible with the model.
    """
    img = Image.open(image_path).convert("RGB")
    img = img.resize((224, 224))
    # Use float32 and an in-place normalization step to reduce peak memory usage.
    img_array = np.asarray(img, dtype=np.float32)
    img_array *= 1.0 / 255.0
    img_array = img_array[None, ...]
    return img_array
