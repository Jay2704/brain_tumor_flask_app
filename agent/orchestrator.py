"""Orchestrator: runs agents in order and returns combined result."""
import time
import uuid
from typing import Any, Dict

from agent.qa_agent import run as qa_run
from agent.vision_agent_tf import run as vision_run
from agent.report_agent_stub import run as report_run
from agent.safety_gate import apply as safety_apply


def run(
    image_path: str,
    model,
    class_labels: list,
    uploaded_image_url: str = "",
) -> Dict[str, Any]:
    """
    Run agents in order. Returns {request_id, qa, vision, report, artifacts, latency_ms}.
    artifacts includes uploaded_image_url.
    """
    start = time.perf_counter()
    request_id = str(uuid.uuid4())

    qa = qa_run(image_path)

    if not qa.get("safe_to_infer", False):
        vision = None
        report = report_run(qa, {})
    else:
        vision = vision_run(image_path, model, class_labels)
        report = report_run(qa, vision)

    report = safety_apply(qa, vision or {}, report)

    artifacts = {"uploaded_image_url": uploaded_image_url}
    latency_ms = (time.perf_counter() - start) * 1000

    return {
        "request_id": request_id,
        "qa": qa,
        "vision": vision,
        "report": report,
        "artifacts": artifacts,
        "latency_ms": round(latency_ms, 2),
    }
