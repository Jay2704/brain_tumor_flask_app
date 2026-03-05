"""Safety gate: override report when QA fails or confidence < 0.60, always add disclaimer."""
from typing import Any, Dict


DISCLAIMER = "Educational demo only. Not medical advice."


def apply(qa: Dict[str, Any], vision: Dict[str, Any], report: Dict[str, Any]) -> Dict[str, Any]:
    """
    Override report output when QA fails or confidence < 0.60.
    Always ensures limitations contains the disclaimer.
    """
    result = dict(report)

    if not qa.get("safe_to_infer", False):
        result["impression"] = "Inconclusive due to image quality"
        result["urgency"] = "low"
        result["findings"] = "; ".join(qa.get("warnings", []) or ["Image quality insufficient for analysis."])
        result["next_steps"] = ["Obtain higher quality image.", "Consult a healthcare provider for clinical evaluation."]

    elif vision and vision.get("confidence", 0) < 0.60:
        result["impression"] = "Uncertain classification"
        result["urgency"] = "medium"
        result["findings"] = f"Model prediction: {vision.get('label', 'unknown')} (confidence {vision.get('confidence', 0):.2f}). Quality score: {qa.get('quality_score', 0):.2f}."
        result["next_steps"] = ["Consider repeat imaging or expert review.", "Consult a healthcare provider."]

    result["limitations"] = DISCLAIMER
    return result
