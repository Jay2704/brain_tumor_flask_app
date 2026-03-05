"""QA agent: image quality checks using PIL + numpy."""
import numpy as np
from PIL import Image


def run(image_path: str) -> dict:
    """
    Run QA checks on image. Returns {safe_to_infer, quality_score, warnings}.
    """
    warnings = []
    try:
        img = Image.open(image_path).convert("RGB")
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
