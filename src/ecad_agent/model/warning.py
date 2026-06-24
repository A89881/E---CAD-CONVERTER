"""Warning model."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

Severity = Literal["info", "warning", "error"]


@dataclass(slots=True)
class WarningMessage:
    """A warning carried through import, validation, export, or AI review."""

    code: str
    message: str
    severity: Severity = "warning"
    subject: str | None = None

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "code": self.code,
            "message": self.message,
            "severity": self.severity,
        }
        if self.subject is not None:
            payload["subject"] = self.subject
        return payload

    @classmethod
    def from_dict(cls, payload: dict[str, Any]) -> WarningMessage:
        severity = payload.get("severity", "warning")
        if severity not in {"info", "warning", "error"}:
            severity = "warning"
        return cls(
            code=str(payload["code"]),
            message=str(payload["message"]),
            severity=severity,
            subject=payload.get("subject"),
        )
