"""Model configurations (protocol §3) and transport clients. Parameters here are the protocol's, verbatim."""
from __future__ import annotations

import os
import time

import requests

from .common import TOOLS

LOCAL_URL = "http://127.0.0.1:8089"
LOCAL_SERVER_ARGS = ["-ngl", "99", "-c", "8192", "-np", "1", "--seed", "1234", "--no-cache-prompt", "--jinja",
                     "--host", "127.0.0.1", "--port", "8089"]
LOCAL_PARAMS = {"n_predict": 16, "temperature": -1, "n_probs": 20, "cache_prompt": False, "seed": 1234}

# "auroc": whether AUROC is reported for the model (§7). Qwen3-4B is hard-label only (D11): its §7.1 score is still
# extracted, but only its coverage is reported, as a diagnostic. Not part of the request parameters.
MODELS = {
    "qwen3-4b": {"kind": "local", "gguf": "Qwen3-4B-Instruct-2507-Q4_K_M.gguf",
                 "hf": "unsloth/Qwen3-4B-Instruct-2507-GGUF@a06e946bb6b655725eafa393f4a9745d460374c9",
                 "template_kwargs": {}, "auroc": False},
    "llama-3.2-3b": {"kind": "local", "gguf": "Llama-3.2-3B-Instruct-Q4_K_M.gguf", "auroc": True,
                     "hf": "bartowski/Llama-3.2-3B-Instruct-GGUF@5ab33fa94d1d04e903623ae72c95d1696f09f9e8",
                     # §3 / P4: the Llama 3.2 template inserts today's date ("Today Date: 09 Oct 2026" on 2026-10-09),
                     # so the date is pinned as the protocol specifies.
                     "template_kwargs": {"date_string": "26 Jul 2024"}},
    "gpt-oss-120b": {"kind": "groq", "model_id": "openai/gpt-oss-120b", "auroc": False,
                     "params": {"temperature": 0, "max_completion_tokens": 1024, "reasoning_effort": "low",
                                "include_reasoning": True, "seed": 1234}},
    "claude-haiku-4.5": {"kind": "anthropic", "model_id": "claude-haiku-4-5-20251001", "auroc": False,
                         "params": {"temperature": 0.0, "max_tokens": 16}},
}


def model_params(model_key: str) -> dict:
    m = MODELS[model_key]
    if m["kind"] == "local":
        return {**LOCAL_PARAMS, "gguf": m["gguf"], "template_kwargs": m["template_kwargs"],
                "server_args": LOCAL_SERVER_ARGS}
    return {**m["params"], "model_id": m["model_id"]}


class TransportError(Exception):
    """Retryable failure (connection, timeout, 408/409/429/5xx)."""

    def __init__(self, msg, status=None, retry_after=None):
        super().__init__(msg)
        self.status, self.retry_after = status, retry_after


class FatalError(Exception):
    """Non-retryable failure (400/401/403/404): stops the run."""


def _check(resp: requests.Response):
    if resp.status_code in (400, 401, 403, 404):
        raise FatalError(f"HTTP {resp.status_code}: {resp.text[:300]}")
    if resp.status_code in (408, 409, 429) or resp.status_code >= 500:
        ra = resp.headers.get("retry-after")
        raise TransportError(f"HTTP {resp.status_code}", resp.status_code, float(ra) if ra else None)
    resp.raise_for_status()


class LocalClient:
    def __init__(self, url: str = LOCAL_URL, timeout: float = 600):
        self.url, self.timeout = url, timeout

    def _post(self, path, body):
        try:
            r = requests.post(self.url + path, json=body, timeout=self.timeout)
        except requests.RequestException as e:
            raise TransportError(repr(e)) from e
        _check(r)
        return r.json()

    def props(self) -> dict:
        return requests.get(self.url + "/props", timeout=30).json()

    def apply_template(self, msgs, template_kwargs=None) -> str:
        body = {"messages": msgs}
        if template_kwargs:
            body["chat_template_kwargs"] = template_kwargs
        return self._post("/apply-template", body)["prompt"]

    def tokenize(self, text: str, with_pieces: bool = False) -> list:
        return self._post("/tokenize", {"content": text, "add_special": False, "parse_special": True,
                                        "with_pieces": with_pieces})["tokens"]

    def completion(self, prompt: str) -> dict:
        body = {"prompt": prompt, **{k: LOCAL_PARAMS[k] for k in LOCAL_PARAMS}}
        return self._post("/completion", body)

    def chat(self, msgs) -> dict:
        """Pilot-style /v1/chat/completions call, used only for the P5 equivalence check."""
        return self._post("/v1/chat/completions",
                          {"messages": msgs, "temperature": 0, "max_tokens": 16, "stream": False})


class GroqClient:
    URL = "https://api.groq.com/openai/v1/chat/completions"

    def __init__(self, timeout: float = 120):
        key = os.environ.get("GROQ_API_KEY")
        if not key:
            raise FatalError("GROQ_API_KEY is not set")
        self.headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
        self.timeout = timeout

    def chat(self, msgs, params: dict) -> tuple[dict, dict]:
        body = {"model": params["model_id"], "messages": msgs,
                **{k: v for k, v in params.items() if k != "model_id"}}
        try:
            r = requests.post(self.URL, json=body, headers=self.headers, timeout=self.timeout)
        except requests.RequestException as e:
            raise TransportError(repr(e)) from e
        _check(r)
        return r.json(), {"request_id": r.headers.get("x-request-id")}


class AnthropicClient:
    def __init__(self, timeout: float = 60):
        import anthropic  # pinned in requirements.txt
        self.anthropic = anthropic
        # SDK auto-retries disabled: the harness logs and retries every attempt itself (§3).
        self.client = anthropic.Anthropic(max_retries=0, timeout=timeout)

    def create(self, system: str, user: str, params: dict):
        a = self.anthropic
        try:
            return self.client.messages.create(
                model=params["model_id"], max_tokens=params["max_tokens"], temperature=params["temperature"],
                system=system, messages=[{"role": "user", "content": user}])
        except (a.BadRequestError, a.AuthenticationError, a.PermissionDeniedError, a.NotFoundError) as e:
            raise FatalError(repr(e)) from e
        except a.RateLimitError as e:
            ra = e.response.headers.get("retry-after") if e.response is not None else None
            raise TransportError(repr(e), 429, float(ra) if ra else None) from e
        except a.APIStatusError as e:
            if e.status_code in (408, 409) or e.status_code >= 500:
                raise TransportError(repr(e), e.status_code) from e
            raise FatalError(repr(e)) from e
        except (a.APIConnectionError, a.APITimeoutError) as e:
            raise TransportError(repr(e)) from e


def wait_for_local(url: str = LOCAL_URL, timeout_s: float = 180) -> None:
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        try:
            if requests.get(url + "/health", timeout=5).json().get("status") == "ok":
                return
        except (requests.RequestException, ValueError):
            pass
        time.sleep(2)
    raise SystemExit("local server did not become healthy")


def server_command(model_key: str) -> list[str]:
    exe = TOOLS / "llama.cpp" / "llama-server.exe"
    return [str(exe), "-m", str(TOOLS / "models" / MODELS[model_key]["gguf"]), *LOCAL_SERVER_ARGS]
