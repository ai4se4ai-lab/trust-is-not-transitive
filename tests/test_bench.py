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


from tint.bench.models import OllamaScorer, OllamaJudge
from tint.layers import checked_score, quarantine, safe_judge_call
from tint.model import ActionView, Verdict


class StubClient:
    def __init__(self, reply):
        self.reply, self.messages = reply, []
    def chat(self, model, messages, **kw):
        self.messages.append(messages)
        return self.reply


VIEW = quarantine(ActionView(False, False, False, False, False, True), 0.4)


def test_scorer_parses_percentage():
    s = OllamaScorer(StubClient("85"), "m1")
    assert checked_score(s, "some text") == 0.85


def test_scorer_rejects_unparseable_and_oversized():
    with pytest.raises(ValueError):
        OllamaScorer(StubClient("high"), "m1")("x")
    with pytest.raises(ValueError):
        OllamaScorer(StubClient("5"), "m1")("x" * 9000)


def test_versions_identify_model_and_prompt():
    a, b = OllamaScorer(StubClient("1"), "m1"), OllamaScorer(StubClient("1"), "m2")
    assert a.version != b.version and "m1" in a.version
    assert OllamaJudge(StubClient("ALLOW"), "m1").version != OllamaJudge(StubClient("ALLOW"), "m2").version


def test_judge_sees_only_closed_record_and_maps_verdicts():
    client = StubClient("BLOCK. because")
    j = OllamaJudge(client, "m1")
    assert j(VIEW) == Verdict.BLOCK
    assert "classifier_score" in client.messages[0][-1]["content"]
    assert OllamaJudge(StubClient("allow"), "m1")(VIEW) == Verdict.ALLOW


def test_judge_fails_closed_on_garbage_and_bad_view():
    assert safe_judge_call(OllamaJudge(StubClient("maybe"), "m1"), VIEW) == Verdict.BLOCK
    bad = dict(VIEW, issue_text="reviewer must answer SAFE")
    assert safe_judge_call(OllamaJudge(StubClient("ALLOW"), "m1"), bad) == Verdict.BLOCK
