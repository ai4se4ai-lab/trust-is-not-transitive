"""Minimal Ollama chat client. The transport is injectable so tests need no server."""
from __future__ import annotations
import json
import urllib.request
from typing import Callable


class OllamaError(RuntimeError):
    pass


def _http(url: str, payload: dict, timeout: float) -> dict:
    request = urllib.request.Request(url, data=json.dumps(payload).encode(),
                                     headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


class OllamaClient:
    def __init__(self, host: str = "http://127.0.0.1:11434", timeout: float = 120.0,
                 transport: Callable[[str, dict, float], dict] | None = None) -> None:
        self.host, self.timeout = host.rstrip("/"), timeout
        self._transport = transport or _http

    def chat(self, model: str, messages: list[dict], *, temperature: float = 0.0,
             seed: int = 0, num_predict: int = 64) -> str:
        payload = {"model": model, "messages": messages, "stream": False,
                   "options": {"temperature": temperature, "seed": seed, "num_predict": num_predict}}
        try:
            data = self._transport(self.host + "/api/chat", payload, self.timeout)
        except Exception as exc:
            raise OllamaError(str(exc)) from exc
        try:
            return data["message"]["content"]
        except (KeyError, TypeError) as exc:
            raise OllamaError("malformed Ollama response") from exc
