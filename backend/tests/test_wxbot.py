"""The Ask panel's call to the 马莫百科 WeChat bot.

No real bot is called: urlopen is replaced, so these run without a network.
"""
from __future__ import annotations

import io
import json
import urllib.error

import pytest
from app.core import throttle, wxbot
from app.core.config import get_settings


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


@pytest.fixture
def bot(monkeypatch):
    settings = get_settings()
    monkeypatch.setattr(settings, "wxbot_url", "https://bot.example/")
    monkeypatch.setattr(settings, "wxbot_web_secret", "s3cret")
    sent = []

    def answer_with(body=None, error=None):
        def fake(request, timeout):
            sent.append((request, timeout))
            if error:
                raise error
            return FakeResponse(json.dumps(body).encode())
        monkeypatch.setattr(wxbot.urllib.request, "urlopen", fake)
    return sent, answer_with


def test_the_question_goes_to_the_bot_with_the_token(bot):
    sent, answer_with = bot
    answer_with({"route": "qa", "reply": "加微信 MonashGuide"})
    assert wxbot.ask("怎么进群", "v1") == wxbot.BotAnswer("qa", "加微信 MonashGuide")
    request, _ = sent[0]
    assert request.full_url == "https://bot.example/web/ask"
    assert request.get_header("Authorization") == "Bearer s3cret"
    assert json.loads(request.data) == {"question": "怎么进群", "visitor": "v1"}


def test_a_miss_has_no_reply(bot):
    _, answer_with = bot
    answer_with({"route": "miss", "reply": None})
    assert wxbot.ask("食堂哪家好吃", "v1") == wxbot.BotAnswer("miss", None)


def test_a_bot_that_is_down_or_refuses_is_no_answer(bot):
    _, answer_with = bot
    answer_with(error=urllib.error.URLError("refused"))
    assert wxbot.ask("怎么进群", "v1") is None
    answer_with(error=urllib.error.HTTPError("u", 401, "no", {}, None))
    assert wxbot.ask("怎么进群", "v1") is None
    answer_with(error=TimeoutError())
    assert wxbot.ask("怎么进群", "v1") is None


def test_the_bot_limiting_a_visitor_is_said_so(bot):
    _, answer_with = bot
    answer_with(error=urllib.error.HTTPError("u", 429, "slow down", {}, None))
    assert wxbot.ask("怎么进群", "v1") == wxbot.BotAnswer("rate_limited", None)


def test_nothing_is_sent_when_the_bot_is_not_configured(monkeypatch):
    monkeypatch.setattr(get_settings(), "wxbot_url", "")
    called = []
    monkeypatch.setattr(wxbot.urllib.request, "urlopen", lambda *a, **k: called.append(a))
    assert wxbot.ask("怎么进群", "v1") is None and called == []


def test_the_endpoint_says_when_there_is_no_bot(client, monkeypatch):
    monkeypatch.setattr(get_settings(), "wxbot_url", "")
    body = client.post("/api/v1/assistant/bot", json={"query": "怎么进群", "visitor": "v1"}).json()
    assert body == {"available": False, "route": None, "reply": None}


def test_the_endpoint_passes_the_reply_on(client, bot):
    _, answer_with = bot
    answer_with({"route": "article", "reply": "马莫百科文章"})
    body = client.post("/api/v1/assistant/bot", json={"query": "交换", "visitor": "v1"}).json()
    assert body == {"available": True, "route": "article", "reply": "马莫百科文章"}


def test_one_network_is_limited(client, bot, monkeypatch):
    _, answer_with = bot
    answer_with({"route": "miss", "reply": None})
    monkeypatch.setattr(throttle, "BOT_QUESTIONS_PER_ADDRESS", throttle.Limit(throttle.BOT_QUESTION_IP, 2, 3600))
    codes = [client.post("/api/v1/assistant/bot", json={"query": "q", "visitor": f"v{n}"}).status_code
             for n in range(3)]
    assert codes == [200, 200, 429]
