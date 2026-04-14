from __future__ import annotations

import os
from dataclasses import dataclass
import requests


@dataclass(frozen=True)
class OllamaSettings:
    base_url: str
    model: str
    timeout_s: float = 120.0


def load_ollama_settings() -> OllamaSettings:
    timeout_raw = os.getenv("OLLAMA_TIMEOUT_S", "").strip()
    try:
        timeout_s = float(timeout_raw) if timeout_raw else 240.0
    except ValueError:
        timeout_s = 240.0

    return OllamaSettings(
        base_url=os.getenv("OLLAMA_BASE_URL", "cloud"),  # cloud = Groq
        model=os.getenv("OLLAMA_MODEL", "llama3"),
        timeout_s=timeout_s,
    )


def create_completion_json(
    *,
    base_url: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    temperature: float,
    timeout_s: float,
) -> str:

    model_name = (model or "").strip() or "llama3"
    prompt = f"{system_prompt.strip()}\n\n{user_prompt.strip()}".strip()

    # =========================================================
    # 🔵 CLOUD MODE → GROQ
    # =========================================================
    if "localhost" not in base_url:
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            return "❌ Missing GROQ_API_KEY"

        try:
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": "llama3-8b-instant"
                    "messages": [
                        {"role": "system", "content": system_prompt.strip()},
                        {"role": "user", "content": user_prompt.strip()},
                    ],
                    "temperature": float(temperature),
                },
                timeout=60,
            )

            # ✅ SAFE PARSING (FIX)
            try:
                data = response.json()
            except Exception:
                return f"❌ Invalid JSON response: {response.text}"

            # ✅ HANDLE API ERROR
            if response.status_code != 200:
                return f"❌ API Error {response.status_code}: {data}"

            # ✅ FIX FOR 'choices' ERROR
            if "choices" not in data:
                return f"❌ Unexpected response: {data}"

            try:
                return data["choices"][0]["message"]["content"]
            except Exception:
                return f"❌ Parsing error: {data}"

        except Exception as e:
            return f"❌ API request failed: {str(e)}"

    # =========================================================
    # 🟢 LOCAL MODE → OLLAMA
    # =========================================================
    url_base = base_url.rstrip("/")

    try:
        response = requests.post(
            f"{url_base}/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
            },
            timeout=timeout_s,
        )

        if response.status_code != 200:
            return f"❌ Ollama error: {response.text}"

        try:
            data = response.json()
        except Exception:
            return f"❌ Invalid Ollama response: {response.text}"

        result = str(data.get("response", "")).strip()

        if not result:
            return "⚠️ Empty response from Ollama"

        return result

    except Exception as e:
        return f"❌ Ollama connection error: {str(e)}"