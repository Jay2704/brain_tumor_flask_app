"""Response schemas for the brain tumor analysis pipeline (dataclasses, no extra deps)."""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class QAResult:
    safe_to_infer: bool
    quality_score: float
    warnings: List[str]


@dataclass
class VisionResult:
    label: str
    confidence: float
    probs: Dict[str, float]


@dataclass
class ReportResult:
    findings: str
    impression: str
    next_steps: List[str]
    limitations: str
    urgency: str


@dataclass
class OrchestratorResult:
    request_id: str
    qa: Dict[str, Any]
    vision: Optional[Dict[str, Any]]
    report: Dict[str, Any]
    artifacts: Dict[str, Any] = field(default_factory=dict)
    latency_ms: float = 0.0
