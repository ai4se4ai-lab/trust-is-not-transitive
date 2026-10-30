import pytest
from tint.bench.ollama import OllamaClient, OllamaError


def fake(reply):
    calls = []
    def transport(url, payload, timeout):
        calls.append((url, payload, timeout))
        return reply
    transport.calls = calls
    return transport


def test_chat_returns_content_and_sends_deterministic_options():
    t = fake({"message": {"content": "hello"}})
    client = OllamaClient("http://h:1/", timeout=5, transport=t)
    assert client.chat("m", [{"role": "user", "content": "x"}], seed=7) == "hello"
    url, payload, timeout = t.calls[0]
    assert url == "http://h:1/api/chat" and timeout == 5
    assert payload["stream"] is False and payload["model"] == "m"
    assert payload["options"] == {"temperature": 0.0, "seed": 7, "num_predict": 64}


def test_malformed_reply_raises():
    client = OllamaClient(transport=fake({"oops": 1}))
    with pytest.raises(OllamaError):
        client.chat("m", [])


def test_transport_failure_is_wrapped():
    def boom(url, payload, timeout):
        raise OSError("down")
    with pytest.raises(OllamaError):
        OllamaClient(transport=boom).chat("m", [])
