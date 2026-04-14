from __future__ import annotations

import datetime as _dt
from typing import Optional

import streamlit as st

from utils.report import BugReport


def page_header() -> None:
    st.set_page_config(
        page_title="AI Bug Reproduction Assistant",
        page_icon="🛠️",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    st.title("AI Bug Reproduction Assistant")
    st.caption("Analyze bugs faster with structured AI-powered debugging output.")


def sidebar_settings() -> dict:
    st.sidebar.header("Settings")

    model = st.sidebar.text_input("Model", value=_default("OLLAMA_MODEL", "phi3"))
    temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.2, 0.05)

    st.sidebar.subheader("Context")
    language = st.sidebar.selectbox("Language", ["Python", "JavaScript/TypeScript", "Java", "Go", "C#", "Other"])
    runtime = st.sidebar.text_input("Runtime (optional)", value="")
    framework = st.sidebar.text_input("Framework (optional)", value="")
    os_name = st.sidebar.selectbox("OS", ["Windows", "Linux", "macOS", "Other"], index=0)
    test_framework = st.sidebar.selectbox(
        "Test framework",
        ["pytest", "unittest", "jest", "vitest", "go test", "JUnit", "NUnit", "Other"],
        index=0,
    )

    st.sidebar.subheader("Privacy")
    redact = st.sidebar.checkbox("Redact likely secrets before sending", value=True)

    st.sidebar.subheader("Quality")
    strict_repro = st.sidebar.checkbox(
        "Prefer deterministic reproduction steps (may ask for assumptions)",
        value=True,
    )

    return {
        "model": model.strip() or _default("OLLAMA_MODEL", "phi3"),
        "temperature": float(temperature),
        "language": language,
        "runtime": runtime.strip() or None,
        "framework": framework.strip() or None,
        "os_name": os_name,
        "test_framework": test_framework,
        "redact": redact,
        "strict_repro": strict_repro,
    }


def report_to_markdown(report: BugReport) -> str:
    ts = _dt.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
    lines: list[str] = []
    lines.append(f"# AI Bug Reproduction Assistant Report\n\nGenerated: `{ts}`\n")
    lines.append("## Summary\n")
    lines.append(report.summary.strip() + "\n")
    lines.append("## Root cause\n")
    lines.append(report.root_cause.strip() + "\n")
    lines.append(f"## Confidence\n\n`{report.confidence}`\n")

    lines.append("## Reproduction steps\n")
    if report.reproduction_steps:
        for i, s in enumerate(report.reproduction_steps, start=1):
            lines.append(f"{i}. {s.step.strip()}")
        lines.append("")
    else:
        lines.append("_No steps provided._\n")

    lines.append("## Fixes\n")
    if report.fixes:
        for fx in report.fixes:
            lines.append(f"### {fx.title.strip()}\n")
            lines.append(f"**Risk:** `{fx.risk}`\n\n")
            lines.append(f"**Rationale:** {fx.rationale.strip()}\n\n")
            lines.append("**Patch guidance:**\n")
            lines.append("```")
            lines.append(fx.patch_guidance.rstrip())
            lines.append("```\n")
    else:
        lines.append("_No fixes provided._\n")

    lines.append("## Test case\n")
    if report.test_case:
        tc = report.test_case
        lines.append(f"**Framework:** `{tc.test_framework}`\n\n")
        lines.append(f"**Suggested file:** `{tc.file_name}`\n\n")
        lines.append("```")
        lines.append(tc.code.rstrip())
        lines.append("```\n")
        if tc.notes:
            lines.append(f"**Notes:** {tc.notes.strip()}\n")
    else:
        lines.append("_No test case provided._\n")

    lines.append("## Assumptions\n")
    if report.assumptions:
        for a in report.assumptions:
            lines.append(f"- {a.strip()}")
        lines.append("")
    else:
        lines.append("_None._\n")

    lines.append("## Follow-up questions\n")
    if report.follow_up_questions:
        for q in report.follow_up_questions:
            lines.append(f"- {q.strip()}")
        lines.append("")
    else:
        lines.append("_None._\n")

    return "\n".join(lines).strip() + "\n"


def _default(env_key: str, fallback: str) -> str:
    import os

    v = os.getenv(env_key, "").strip()
    return v or fallback

