"""Warning and ValidationResult models.

Every importer, the integrity checker, and (later) the validation engine speak
the same Warning vocabulary so the AI layer and reports have one structure to
consume.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class Severity(str, Enum):
    """How serious an issue is. 'error' means the model is not trustworthy."""

    INFO = "info"
    WARNING = "warning"
    ERROR = "error"


class Warning(BaseModel):
    """A single machine-readable issue.

    ``code`` is a stable, greppable identifier (e.g. 'UNCONNECTED_PIN') so the
    AI layer can map it to human-friendly explanations without parsing prose.
    ``refs`` names the affected components / nets / pins (e.g. ['U1', 'R1.2']).
    """

    model_config = ConfigDict(extra="forbid")

    code: str = Field(..., description="Stable machine code, e.g. 'UNCONNECTED_PIN'.")
    severity: Severity = Field(default=Severity.WARNING)
    message: str = Field(..., description="Human-readable description.")
    refs: list[str] = Field(
        default_factory=list,
        description="Affected components / nets / pins, e.g. ['U1', 'NET_A', 'R1.2'].",
    )


class ValidationResult(BaseModel):
    """Outcome of a validation pass. Filled in by Workstream D; defined here so
    the model package owns the shared vocabulary."""

    model_config = ConfigDict(extra="forbid")

    passed: bool = Field(..., description="True if no error-severity issues were found.")
    summary: str | None = Field(None, description="One-line human summary.")
    warnings: list[Warning] = Field(default_factory=list)

    @classmethod
    def from_warnings(
        cls,
        warnings: list[Warning],
        summary: str | None = None,
    ) -> ValidationResult:
        """Build a result; ``passed`` is False iff any warning is an error."""
        passed = not any(w.severity is Severity.ERROR for w in warnings)
        return cls(passed=passed, warnings=warnings, summary=summary)
