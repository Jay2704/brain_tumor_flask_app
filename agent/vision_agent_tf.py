"""Vision agent: TensorFlow model inference."""
import gc
import numpy as np

from ml.preprocess import preprocess_image

# Model output order: glioma, meningioma, no_tumor, pituitary (synced with image_data folder names)
CLASS_LABELS = ["glioma", "meningioma", "no_tumor", "pituitary"]


def run(image_path: str, model, class_labels: list = None) -> dict:
    """
    Run vision inference. Returns {label, confidence, probs}.
    Uses no_tumor (underscore) in label keys.
    """
    if class_labels is None:
        class_labels = CLASS_LABELS
    processed = preprocess_image(image_path)
    try:
        preds = model.predict(processed, verbose=0)[0]
        probs = {k: float(v) for k, v in zip(class_labels, preds)}
        idx = int(np.argmax(preds))
        label = class_labels[idx]
        confidence = float(preds[idx])
        return {"label": label, "confidence": confidence, "probs": probs}
    finally:
        # Free per-request arrays promptly on low-memory deployments.
        del processed
        gc.collect()
