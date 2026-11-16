"""One entry point for AI calls. Picks the provider from AI_PROVIDER and records timing.

    from app.clients import ai
    text = await ai.generate(prompt)
    vectors = await ai.embed_many(texts)

Timing of every AI call in a request is collected for the monitoring access log.
"""
import asyncio
import contextvars
import time

from app import config
from app.clients import huggingface, ollama
from app.exceptions import AIUnavailableError

# Per-request AI usage, read by the access-log middleware.
_usage: contextvars.ContextVar[dict | None] = contextvars.ContextVar("ai_usage", default=None)


def start_tracking() -> dict:
    usage = {"calls": 0, "ms": 0, "errors": 0}
    _usage.set(usage)
    return usage


def _record(started: float, failed: bool) -> None:
    usage = _usage.get()
    if usage is None:
        return
    usage["calls"] += 1
    usage["ms"] += int((time.perf_counter() - started) * 1000)
    if failed:
        usage["errors"] += 1


def provider() -> str:
    return "huggingface" if config.AI_PROVIDER == "huggingface" else "ollama"


def runs_locally() -> bool:
    return provider() == "ollama"


def model_name() -> str:
    return config.HF_CHAT_MODEL if provider() == "huggingface" else config.GENERATE_MODEL


def _client():
    return huggingface if provider() == "huggingface" else ollama


async def is_alive() -> bool:
    return await _client().is_alive()


async def generate(prompt: str) -> str:
    t = time.perf_counter()
    try:
        out = await _client().generate(prompt)
    except AIUnavailableError:
        _record(t, failed=True)
        raise
    _record(t, failed=False)
    return out


async def embed_many(texts: list[str]) -> list[list[float]]:
    t = time.perf_counter()
    try:
        if provider() == "huggingface":
            out = await huggingface.embed_many(texts)
        else:
            out = list(await asyncio.gather(*[ollama.embed(x) for x in texts]))
    except AIUnavailableError:
        _record(t, failed=True)
        raise
    _record(t, failed=False)
    return out


async def embed(text: str) -> list[float]:
    return (await embed_many([text]))[0]


def unavailable_message() -> str:
    """Plain-language message for when an AI call fails."""
    if runs_locally():
        return ("The AI assistant isn't running. Start Ollama on your computer "
                "(run “ollama serve”), then try again.")
    return "The AI service isn't responding right now. Please try again in a minute."
