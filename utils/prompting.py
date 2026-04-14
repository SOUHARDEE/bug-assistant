from __future__ import annotations

import json
from typing import Any, Dict, Optional


def build_system_prompt() -> str:
    """
    System prompt focused on producing actionable, structured engineering output.

    Keep it short and unambiguous: the schema is enforced in parsing.
    """

    return (
        "You are an expert software engineer. "
        "Return ONLY valid JSON for the required schema. "
        "Be concise: short fields, minimal lists, no extra commentary."
    )


def _trim(text: str, max_chars: int) -> str:
    value = (text or "").strip()
    if len(value) <= max_chars:
        return value
    return f"{value[:max_chars].rstrip()}\n...[truncated]"


def build_user_prompt(
    *,
    error_logs: str,
    code: str,
    language: str,
    runtime: Optional[str],
    framework: Optional[str],
    os_name: str,
    test_framework: str,
    extra_context: str,
    strict_repro: bool,
) -> str:
    """
    User prompt that includes inputs and strong constraints.

    We include OS and runtime hints because reproduction steps differ drastically
    across environments.
    """

    directives = {
        "strict_repro": bool(strict_repro),
        "preferences": {
            "language": language,
            "runtime": runtime,
            "framework": framework,
            "os": os_name,
            "test_framework": test_framework,
        },
        "output_limits": {
            "max_repro_steps": 4,
            "max_fixes": 3,
            "max_assumptions": 3,
            "max_follow_up_questions": 3,
            "short_text": True,
        },
    }

    compact_schema = {
        "summary": "string",
        "root_cause": "string",
        "confidence": "low|medium|high",
        "reproduction_steps": [{"step": "string"}],
        "fixes": [
            {
                "title": "string",
                "rationale": "string",
                "patch_guidance": "string",
                "risk": "low|medium|high",
            }
        ],
        "test_case": {
            "test_framework": "string",
            "file_name": "string",
            "code": "string",
            "notes": "string|null",
        },
        "assumptions": ["string"],
        "follow_up_questions": ["string"],
    }

    return (
        "Analyze this bug and return JSON only.\n"
        f"directives={json.dumps(directives, separators=(',', ':'))}\n"
        f"error_logs={json.dumps(_trim(error_logs, 6000))}\n"
        f"code={json.dumps(_trim(code, 6000))}\n"
        f"extra_context={json.dumps(_trim(extra_context, 1200))}\n"
        f"schema={json.dumps(compact_schema, separators=(',', ':'))}"
    )


def output_schema() -> Dict[str, Any]:
    """
    A JSON schema-like shape that is easy for LLMs to follow.

    We keep it as a plain object (not strict JSON Schema) to reduce brittleness.
    """

    return {
        "summary": "string",
        "root_cause": "string",
        "confidence": "low|medium|high",
        "reproduction_steps": [{"step": "string"}],
        "fixes": [
            {
                "title": "string",
                "rationale": "string",
                "patch_guidance": "string",
                "risk": "low|medium|high",
            }
        ],
        "test_case": {
            "test_framework": "string",
            "file_name": "string",
            "code": "string",
            "notes": "string|null",
        },
        "assumptions": ["string"],
        "follow_up_questions": ["string"],
    }

