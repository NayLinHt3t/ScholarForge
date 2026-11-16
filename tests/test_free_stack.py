"""Free hosted stack: Groq for chat, FastEmbed on the server for embeddings."""
import sys
import types
from unittest.mock import patch

import pytest

from app import config
from app.clients import ai, groq, local_embed
from app.exceptions import AIUnavailableError

pytestmark = pytest.mark.anyio


@pytest.fixture
def anyio_backend():
    return "asyncio"


class _Resp:
    def __init__(self, status, data):
        self.status_code, self._data, self.text = status, data, str(data)

    def json(self):
        return self._data


class _Client:
    last = {}

    def __init__(self, resp):
        self.resp = resp

    async def __aenter__(self):
        return self

    async def __aexit__(self, *a):
        return False

    async def post(self, url, json=None, headers=None):
        _Client.last = {"url": url, "json": json, "headers": headers}
        return self.resp


def _groq(resp):
    return patch("app.clients.groq.httpx.AsyncClient", lambda **kw: _Client(resp))


@pytest.fixture
def groq_on():
    with patch.object(config, "AI_PROVIDER", "groq"), patch.object(config, "EMBED_PROVIDER", "local"), \
         patch.object(config, "GROQ_API_KEY", "gsk_test"), patch.object(config, "GROQ_MODEL", "openai/gpt-oss-20b"):
        yield


async def test_groq_chat_request(groq_on):
    with _groq(_Resp(200, {"choices": [{"message": {"content": "Hi there"}}]})):
        assert await groq.generate("Hello") == "Hi there"
    assert _Client.last["url"] == "https://api.groq.com/openai/v1/chat/completions"
    assert _Client.last["headers"]["Authorization"] == "Bearer gsk_test"
    assert _Client.last["json"]["model"] == "openai/gpt-oss-20b"
    assert _Client.last["json"]["reasoning_effort"] == "low"


async def test_groq_rate_limit_is_ai_unavailable(groq_on):
    with _groq(_Resp(429, {"error": "rate limit"})):
        with pytest.raises(AIUnavailableError):
            await groq.generate("Hello")


async def test_groq_without_key():
    with patch.object(config, "GROQ_API_KEY", ""):
        assert await groq.is_alive() is False
        with pytest.raises(AIUnavailableError):
            await groq.generate("x")


async def test_facade_uses_groq_and_local_embeddings(groq_on):
    assert ai.provider() == "groq" and ai.embed_provider() == "local"
    assert ai.service_name() == "Groq" and ai.model_name() == "openai/gpt-oss-20b"
    with patch("app.clients.local_embed.embed_many", return_value=[[1.0, 0.0]]) as emb:
        assert await ai.embed_many(["a"]) == [[1.0, 0.0]]
    emb.assert_called_once()


async def test_local_embed_with_fake_fastembed(monkeypatch):
    class FakeModel:
        def __init__(self, model_name, cache_dir=None, threads=None):
            self.name = model_name

        def embed(self, texts, batch_size=None):
            for t in texts:
                yield [float(len(t)), 1.0]

    monkeypatch.setitem(sys.modules, "fastembed", types.SimpleNamespace(TextEmbedding=FakeModel))
    monkeypatch.setattr(local_embed, "_model", None)
    out = await local_embed.embed_many(["ab", "abcd"])
    assert out == [[2.0, 1.0], [4.0, 1.0]]
    assert local_embed._model.name == config.LOCAL_EMBED_MODEL


async def test_local_embed_missing_library(monkeypatch):
    monkeypatch.setitem(sys.modules, "fastembed", None)        # import fails
    monkeypatch.setattr(local_embed, "_model", None)
    with pytest.raises(AIUnavailableError):
        await local_embed.embed_many(["x"])


def test_terms_name_the_hosted_ai_service(anon_client, groq_on):
    body = anon_client.get("/terms").text
    assert "Groq" in body
    assert "done on ScholarForge's own server" in body


async def _coro_impl(v):
    return v


def _coro(v):
    return _coro_impl(v)
