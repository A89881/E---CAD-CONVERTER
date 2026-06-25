"""Validation report models."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from ecad_agent.model.warning import Severity


@dataclass(slots=True)
class ValidationIssue:
    code: str
    message: str
    severity: Severity | str = Severity.WARNING
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


@dataclass(slots=True)
class ValidationReport:
    success: bool
    issues: list[ValidationIssue] = field(default_factory=list)
    stats: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_issues(
        cls,
        issues: list[ValidationIssue],
        stats: dict[str, Any] | None = None,
    ) -> ValidationReport:
        success = all(
            issue.severity != Severity.ERROR and issue.severity != "error"
            for issue in issues
        )
        return cls(success=success, issues=issues, stats=stats or {})

    def to_dict(self) -> dict[str, Any]:
        return {
            "success": self.success,
            "stats": self.stats,
            "issues": [issue.to_dict() for issue in self.issues],
        }

    def to_markdown(self, title: str = "Validation Report") -> str:
        lines = [f"# {title}", "", f"Status: {'PASS' if self.success else 'FAIL'}", ""]

        if self.stats:
            lines.append("## Stats")
            lines.append("")
            for key in sorted(self.stats):
                lines.append(f"- {key}: {self.stats[key]}")
            lines.append("")

        lines.append("## Issues")
        lines.append("")
        if not self.issues:
            lines.append("- None")
        else:
            for issue in self.issues:
                subject = f" ({issue.subject})" if issue.subject else ""
                lines.append(
                    f"- [{issue.severity}] {issue.code}{subject}: {issue.message}"
                )

        return "\n".join(lines) + "\n"
