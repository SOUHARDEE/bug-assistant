from __future__ import annotations

import os
from dataclasses import dataclass
import requests


@dataclass(frozen=True)
class OllamaSettings:
    base_url: str
    model: str
    timeout_s: float = 120.0


class ModelNotRunningError(RuntimeError):
    """Raised when Ollama daemon is unreachable or returns non-200."""


class OllamaRequestError(RuntimeError):
    """Raised when Ollama request fails for other reasons."""


def load_ollama_settings() -> OllamaSettings:
    timeout_raw = os.getenv("OLLAMA_TIMEOUT_S", "").strip()
    try:
        timeout_s = float(timeout_raw) if timeout_raw else 240.0
    except ValueError:
        timeout_s = 240.0

    return OllamaSettings(
        base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        model=os.getenv("OLLAMA_MODEL", "phi3"),
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
    model_name = (model or "").strip() or "phi3"
    prompt = f"{system_prompt.strip()}\n\n{user_prompt.strip()}".strip()
    url_base = base_url.rstrip("/")
    options = {
        "temperature": float(temperature),
        "num_predict": 220,
        "num_ctx": 2048,
        "top_k": 20,
        "top_p": 0.9,
    }
    timeout = float(timeout_s)

    errors: list[str] = []

    try:
        response = requests.post(
            f"{url_base}/api/generate",
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False,
                "format": "json",
                "keep_alive": "5m",
                "options": options,
            },
            timeout=timeout,
        )
        if response.status_code == 200:
            data = response.json()
            result = str(data.get("response", "")).strip()
            if result:
                return result
            errors.append("generate returned empty response")
        else:
            errors.append(f"generate status {response.status_code}: {response.text}")
    except Exception as e:
        errors.append(f"generate failed: {e}")

    # Fallback path: some local setups are more stable on /api/chat.
    try:
        response = requests.post(
            f"{url_base}/api/chat",
            json={
                "model": model_name,
                "stream": False,
                "format": "json",
                "keep_alive": "5m",
                "messages": [
                    {"role": "system", "content": system_prompt.strip()},
                    {"role": "user", "content": user_prompt.strip()},
                ],
                "options": options,
            },
            timeout=timeout,
        )
        if response.status_code != 200:
            errors.append(f"chat status {response.status_code}: {response.text}")
            raise ModelNotRunningError("; ".join(errors))

        data = response.json()
        message = data.get("message") or {}
        result = str(message.get("content", "")).strip()
        if not result:
            errors.append("chat returned empty response")
            raise OllamaRequestError("; ".join(errors))
        return result
    except ModelNotRunningError:
        raise
    except Exception as e:
        errors.append(f"chat failed: {e}")
        raise OllamaRequestError("; ".join(errors)) from e