from __future__ import annotations

import json
import re
from typing import Any, Dict, Optional, Tuple

from pydantic import ValidationError

from utils.report import BugReport


class ModelOutputError(RuntimeError):
    """Raised when the model output cannot be parsed into the expected schema."""


def parse_bug_report(raw_text: str) -> Tuple[BugReport, Dict[str, Any]]:
    """
    Parse model output into a BugReport.

    Returns:
      - parsed BugReport
      - metadata dict (e.g., parsing strategy, recovered JSON)
    """

    raw_text = (raw_text or "").strip()
    if not raw_text:
        raise ModelOutputError("Empty model output.")

    metadata: Dict[str, Any] = {"strategy": None}

    # 1) Try direct JSON
    obj = _try_json_load(raw_text)
    if obj is not None:
        metadata["strategy"] = "direct_json"
        return _validate(obj, metadata)

    # 2) Try extracting the largest JSON object from surrounding text/fences
    extracted = _extract_json_object(raw_text)
    if extracted is not None:
        obj = _try_json_load(extracted)
        if obj is not None:
            metadata["strategy"] = "extracted_json"
            metadata["extracted_json"] = extracted
            return _validate(obj, metadata)

    # 3) Last resort: attempt to repair common issues (trailing commas, smart quotes)
    repaired = _repair_jsonish(raw_text)
    obj = _try_json_load(repaired)
    if obj is not None:
        metadata["strategy"] = "repaired_json"
        metadata["repaired_json"] = repaired
        return _validate(obj, metadata)

    raise ModelOutputError("Could not parse model output as JSON.")


def _validate(obj: Any, metadata: Dict[str, Any]) -> Tuple[BugReport, Dict[str, Any]]:
    try:
        report = BugReport.model_validate(obj)
        return report, metadata
    except ValidationError as e:
        metadata["validation_error"] = str(e)
        raise ModelOutputError("JSON parsed but did not match expected schema.") from e


def _try_json_load(s: str) -> Optional[Any]:
    try:
        return json.loads(s)
    except Exception:
        return None


def _extract_json_object(text: str) -> Optional[str]:
    """
    Extract the most likely JSON object from free-form text.

    This targets common patterns like:
      ```json
      {...}
      ```
    or a response that includes commentary before/after the JSON.
    """

    # Prefer fenced blocks first.
    fence = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text, flags=re.IGNORECASE)
    if fence:
        candidate = fence.group(1).strip()
        if candidate.startswith("{") and candidate.endswith("}"):
            return candidate

    # Otherwise, try greedy match from first "{" to last "}".
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1].strip()
        if candidate.startswith("{") and candidate.endswith("}"):
            return candidate
    return None


def _repair_jsonish(text: str) -> str:
    """
    Repair a few common JSON-adjacent issues.

    We keep this conservative to avoid turning non-JSON into "valid" but wrong JSON.
    """

    s = text.strip()

    # Replace smart quotes with ASCII quotes.
    s = s.replace("“", '"').replace("”", '"').replace("’", "'")

    # Remove trailing commas before } or ].
    s = re.sub(r",(\s*[}\]])", r"\1", s)

    # If fenced, extract inner.
    extracted = _extract_json_object(s)
    return extracted if extracted is not None else s

