from __future__ import annotations

import streamlit as st
from dotenv import load_dotenv

from utils.ollama_client import (
    create_completion_json,
    load_ollama_settings,
)
from utils.prompting import build_system_prompt, build_user_prompt
from utils.redaction import redact_secrets
from utils.ui import page_header, sidebar_settings


def main() -> None:
    load_dotenv()
    _init_ui_state()

    page_header()
    settings = sidebar_settings()
    st.markdown("---")

    col1, col2 = st.columns(2)

    # -------- LEFT PANEL --------
    with col1:
        st.subheader("🧾 Inputs")

        if st.button("🧪 Load Sample Bug"):
            _load_sample_bug()

        error_logs = st.text_area("📜 Error Logs", key="error_logs_input")
        code = st.text_area("💻 Code", key="code_input")
        extra_context = st.text_area("🧩 Extra Context", key="extra_context_input")

        if st.button("🚀 Analyze Bug"):
            st.session_state["analysis_requested"] = True

    # -------- RIGHT PANEL --------
    with col2:
        st.subheader("📋 Analysis Result")

        if st.session_state.get("analysis_requested"):

            if not (error_logs.strip() or code.strip()):
                st.warning("Please enter logs or code.")
                return

            logs = redact_secrets(error_logs).redacted_text
            code_clean = redact_secrets(code).redacted_text

            system_prompt = build_system_prompt()

            # ✅ FIXED: pass all required arguments
            user_prompt = build_user_prompt(
                error_logs=logs,
                code=code_clean,
                language="python",
                runtime="",
                framework="",
                os_name="windows",
                test_framework="",
                extra_context=extra_context or "",
                strict_repro=False,
            )

            llm = load_ollama_settings()

            with st.spinner("Analyzing..."):
                result = create_completion_json(
                    base_url=llm.base_url,
                    model=llm.model,
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=0.2,
                    timeout_s=llm.timeout_s,
                )

            st.success("✅ Analysis Complete")
            st.markdown("### 🧠 AI Output")
            st.write(result)

            st.download_button(
                "⬇️ Download Report",
                data=result.encode("utf-8"),
                file_name="ai-bug-report.txt",
                mime="text/plain",
                use_container_width=True,
            )

            st.session_state["analysis_requested"] = False


def _init_ui_state() -> None:
    if "analysis_requested" not in st.session_state:
        st.session_state["analysis_requested"] = False

    if "error_logs_input" not in st.session_state:
        st.session_state["error_logs_input"] = ""

    if "code_input" not in st.session_state:
        st.session_state["code_input"] = ""

    if "extra_context_input" not in st.session_state:
        st.session_state["extra_context_input"] = ""


def _load_sample_bug() -> None:
    st.session_state["error_logs_input"] = """TypeError: unsupported operand type(s) for +: 'int' and 'str'"""

    st.session_state["code_input"] = """a = 5
b = "10"
print(a + b)"""

    st.session_state["extra_context_input"] = "Expect numeric addition"


if __name__ == "__main__":
    main()