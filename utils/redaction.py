from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, List, Tuple


@dataclass(frozen=True)
class RedactionResult:
    redacted_text: str
    redactions_applied: List[str]


# This is intentionally conservative: we want to reduce accidental leakage of
# secrets without over-redacting normal code/logs.
_PATTERNS: List[Tuple[str, re.Pattern[str]]] = [
    (
        "openai_api_key",
        re.compile(r"\b(sk-[A-Za-z0-9]{16,})\b"),
    ),
    (
        "aws_access_key_id",
        re.compile(r"\b(AKIA[0-9A-Z]{16})\b"),
    ),
    (
        "aws_secret_access_key",
        re.compile(
            r"\b(aws_secret_access_key)\s*[:=]\s*([A-Za-z0-9/+=]{20,})\b",
            flags=re.IGNORECASE,
        ),
    ),
    (
        "generic_api_key_assignment",
        re.compile(
            r"\b(api[_-]?key|token|secret)\s*[:=]\s*([\"']?)[A-Za-z0-9_\-]{16,}\2",
            flags=re.IGNORECASE,
        ),
    ),
    (
        "bearer_token",
        re.compile(
            r"\bauthorization\s*:\s*bearer\s+[A-Za-z0-9\-_\.=]{16,}\b",
            flags=re.IGNORECASE,
        ),
    ),
    (
        "private_key_block",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\s\S]+?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    ),
]


def redact_secrets(text: str, enabled: bool = True) -> RedactionResult:
    """
    Redact common secret patterns from a text blob.

    This is best-effort; it is not a substitute for proper secret management.
    """

    if not enabled or not text:
        return RedactionResult(redacted_text=text or "", redactions_applied=[])

    applied: List[str] = []
    redacted = text
    for name, pattern in _PATTERNS:
        if pattern.search(redacted):
            applied.append(name)
            redacted = pattern.sub(lambda m: _replacement(m), redacted)

    return RedactionResult(redacted_text=redacted, redactions_applied=applied)


def _replacement(match: re.Match[str]) -> str:
    # Preserve the left-hand side keys when possible to keep logs readable.
    s = match.group(0)
    if ":" in s or "=" in s:
        # Replace only the value-ish part when it looks like an assignment.
        return re.sub(r"([:=]\s*)(.+)$", r"\1[REDACTED]", s)
    return "[REDACTED]"

