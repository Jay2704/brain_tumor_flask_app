import os
from pathlib import Path

import cv2
import gradio as gr
import numpy as np
from PIL import Image
import tensorflow as tf


MODEL_PATH = os.getenv("MODEL_PATH", "Brain_Tumors_vgg_final.h5")
MODEL_PATH_CANDIDATES = [MODEL_PATH, "models/Brain_Tumors_vgg_final.h5"]
IMAGE_SIZE = (224, 224)
CLASS_NAMES = [
    "Glioma Tumor",
    "Meningioma Tumor",
    "Pituitary Tumor",
    "No Tumor",
]
INV_255 = 1.0 / 255.0
LAST_CONV_LAYER_NAME = None
GRADCAM_MODEL = None

def load_model_at_startup():
    """Load model once at startup, trying a small set of relative paths."""
    last_error = None
    for candidate in MODEL_PATH_CANDIDATES:
        if not os.path.exists(candidate):
            continue
        try:
            model = tf.keras.models.load_model(candidate, compile=False)
            return model, candidate, None
        except Exception as exc:
            last_error = str(exc)
    if last_error is None:
        last_error = (
            "Model file not found. Expected one of: "
            + ", ".join(MODEL_PATH_CANDIDATES)
        )
    return None, MODEL_PATH, last_error


# Load model once at server startup (module import time).
MODEL, RESOLVED_MODEL_PATH, MODEL_LOAD_ERROR = load_model_at_startup()


def find_last_conv_layer_name(model) -> str:
    """Return the last Conv2D layer name for Grad-CAM."""
    for layer in reversed(model.layers):
        if isinstance(layer, tf.keras.layers.Conv2D):
            return layer.name
    raise ValueError("No Conv2D layer found in model.")


if MODEL is not None:
    try:
        LAST_CONV_LAYER_NAME = find_last_conv_layer_name(MODEL)
        GRADCAM_MODEL = tf.keras.models.Model(
            inputs=MODEL.inputs,
            outputs=[MODEL.get_layer(LAST_CONV_LAYER_NAME).output, MODEL.output],
        )
    except Exception:
        LAST_CONV_LAYER_NAME = None
        GRADCAM_MODEL = None


def get_example_images():
    """Collect optional examples from ./examples for portable Spaces setup."""
    examples_dir = Path(os.getenv("EXAMPLES_DIR", "examples"))
    if not examples_dir.exists():
        return []

    example_paths = []
    for ext in ("*.jpg", "*.jpeg", "*.png"):
        example_paths.extend(sorted(examples_dir.glob(ext)))
    return [str(path) for path in example_paths[:8]]


def preprocess_image(image: Image.Image) -> np.ndarray:
    """Prepare image for model inference: RGB, 224x224, float32, normalized, batched."""
    processed = image.convert("RGB").resize(IMAGE_SIZE)
    image_array = np.asarray(processed, dtype=np.float32)
    image_array *= INV_255
    return np.expand_dims(image_array, axis=0)


def generate_gradcam_overlay(
    original_image: Image.Image,
    image_batch: np.ndarray,
    class_index: int,
) -> Image.Image:
    """Generate a Grad-CAM heatmap overlay for the selected class."""
    if GRADCAM_MODEL is None:
        return original_image.convert("RGB").resize(IMAGE_SIZE)

    input_tensor = tf.convert_to_tensor(image_batch)
    with tf.GradientTape() as tape:
        conv_outputs, predictions = GRADCAM_MODEL(input_tensor, training=False)
        loss = predictions[:, class_index]

    grads = tape.gradient(loss, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
    conv_activations = conv_outputs[0]
    heatmap = tf.reduce_sum(conv_activations * pooled_grads, axis=-1)
    heatmap = tf.maximum(heatmap, 0)
    max_val = tf.reduce_max(heatmap)
    if float(max_val) > 0:
        heatmap = heatmap / max_val

    heatmap_np = heatmap.numpy()
    heatmap_np = cv2.resize(heatmap_np, IMAGE_SIZE)
    heatmap_uint8 = np.uint8(255 * heatmap_np)
    heatmap_color = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
    heatmap_color = cv2.cvtColor(heatmap_color, cv2.COLOR_BGR2RGB)

    base_img = np.asarray(
        original_image.convert("RGB").resize(IMAGE_SIZE), dtype=np.uint8
    )
    overlay = cv2.addWeighted(base_img, 0.6, heatmap_color, 0.4, 0)
    return Image.fromarray(overlay)


def predict(image: Image.Image):
    if image is None:
        raise gr.Error("Please upload an MRI image.")

    if MODEL is None:
        raise gr.Error(
            f"Model failed to load from '{RESOLVED_MODEL_PATH}'. Details: {MODEL_LOAD_ERROR}"
        )

    image_batch = preprocess_image(image)

    # Call the model directly to avoid predict() overhead in single-request inference.
    preds = MODEL(image_batch, training=False).numpy()[0]
    idx = int(np.argmax(preds))
    predicted_label = CLASS_NAMES[idx]
    confidence = float(preds[idx])
    confidence_pct = round(confidence * 100, 2)
    gradcam_image = generate_gradcam_overlay(image, image_batch, idx)

    probabilities = {
        class_name: round(float(score) * 100, 2)
        for class_name, score in zip(CLASS_NAMES, preds)
    }

    chart_data = {
        "Class": CLASS_NAMES,
        "Confidence (%)": [probabilities[name] for name in CLASS_NAMES],
    }

    return (
        image,
        predicted_label,
        confidence_pct,
        probabilities,
        chart_data,
        gradcam_image,
    )


with gr.Blocks(theme=gr.themes.Soft(), title="Brain Tumor Detection AI") as demo:
    gr.Markdown(
        """
        # Brain Tumor Detection AI
        Deep learning MRI classifier built with TensorFlow and Gradio.
        Upload a brain MRI image to receive the predicted class, confidence score,
        and probability distribution across all tumor categories.
        """
    )

    with gr.Row():
        with gr.Column(scale=1):
            image_input = gr.Image(type="pil", label="Upload MRI Image")
            submit_btn = gr.Button("Run AI Analysis", variant="primary")
            clear_btn = gr.Button("Clear")

            example_images = get_example_images()
            if example_images:
                gr.Examples(
                    examples=example_images,
                    inputs=image_input,
                    label="Example MRI Images",
                )

        with gr.Column(scale=1):
            image_output = gr.Image(type="pil", label="Uploaded Image")
            predicted_label_output = gr.Textbox(label="Predicted Label")
            confidence_output = gr.Number(label="Confidence Score (%)")

    with gr.Row():
        probabilities_output = gr.Label(
            label="Probability Scores (All Classes)"
        )
        chart_output = gr.BarPlot(
            x="Class",
            y="Confidence (%)",
            title="Confidence Bar Chart",
            vertical=False,
            y_lim=[0, 100],
        )

    with gr.Row():
        gradcam_output = gr.Image(
            type="pil",
            label="Grad-CAM (Model Attention Overlay)",
        )

    submit_btn.click(
        fn=predict,
        inputs=image_input,
        outputs=[
            image_output,
            predicted_label_output,
            confidence_output,
            probabilities_output,
            chart_output,
            gradcam_output,
        ],
    )

    clear_btn.click(
        fn=lambda: (None, "", None, None, None, None),
        inputs=None,
        outputs=[
            image_output,
            predicted_label_output,
            confidence_output,
            probabilities_output,
            chart_output,
            gradcam_output,
        ],
    )


if __name__ == "__main__":
    demo.launch()
