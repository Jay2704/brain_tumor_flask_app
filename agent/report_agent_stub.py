"""Report agent stub: deterministic report generation (no LLM)."""
from typing import Any, Dict


def run(qa: Dict[str, Any], vision: Dict[str, Any]) -> dict:
    """
    Generate report deterministically. Returns {findings, impression, next_steps, limitations, urgency}.
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
