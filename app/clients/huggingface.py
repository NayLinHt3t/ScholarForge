"""Hugging Face Inference Providers client (used when the app is hosted).

Chat:       POST {HF_BASE_URL}/v1/chat/completions             (OpenAI-compatible)
Embeddings: POST {HF_BASE_URL}/hf-inference/models/{model}/pipeline/feature-extraction
Both need a fine-grained token with the "Make calls to Inference Providers" permission.
"""
import logging

import httpx

from app import config
from app.exceptions import AIUnavailableError

log = logging.getLogger(__name__)

_TIMEOUT = httpx.Timeout(90.0, connect=10.0)


def _headers() -> dict:
    return {"Authorization": f"Bearer {config.HF_TOKEN}", "Content-Type": "application/json"}


def _raise_for(r: httpx.Response, what: str) -> None:
    if r.status_code < 400:
        return
    # Never log the token; log only status and a short body excerpt.
    log.warning("hf.%s.error status=%s body=%s", what, r.status_code, r.text[:200])
    raise AIUnavailableError(f"Hugging Face {what} failed with HTTP {r.status_code}")


async def is_alive() -> bool:
    """Cheap check: is the provider configured? (No network call — this runs before every search.)"""
    return bool(config.HF_TOKEN)


async def generate(prompt: str) -> str:
    if not config.HF_TOKEN:
        raise AIUnavailableError("HF_TOKEN is not set")
    payload = {
        "model": config.HF_CHAT_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 900,
        "temperature": 0.3,
        "stream": False,
    }
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.post(f"{config.HF_BASE_URL}/v1/chat/completions", json=payload, headers=_headers())
    except httpx.HTTPError as e:
        raise AIUnavailableError(f"Hugging Face unreachable: {type(e).__name__}") from e
    _raise_for(r, "chat")
    try:
        return r.json()["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, ValueError) as e:
        raise AIUnavailableError("Unexpected response from Hugging Face chat") from e


async def embed_many(texts: list[str]) -> list[list[float]]:
    if not config.HF_TOKEN:
        raise AIUnavailableError("HF_TOKEN is not set")
    if not texts:
        return []
    url = f"{config.HF_BASE_URL}/hf-inference/models/{config.HF_EMBED_MODEL}/pipeline/feature-extraction"
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.post(url, json={"inputs": texts, "normalize": True, "truncate": True}, headers=_headers())
    except httpx.HTTPError as e:
        raise AIUnavailableError(f"Hugging Face unreachable: {type(e).__name__}") from e
    _raise_for(r, "embeddings")
    data = r.json()
    if not isinstance(data, list) or len(data) != len(texts):
        raise AIUnavailableError("Unexpected response from Hugging Face embeddings")
    # Some models return token-level vectors ([[...], ...] per input) — mean-pool them.
    out: list[list[float]] = []
    for vec in data:
        if vec and isinstance(vec[0], list):
            n = len(vec)
            vec = [sum(col) / n for col in zip(*vec)]
        out.append([float(x) for x in vec])
    return out


async def embed(text: str) -> list[float]:
    return (await embed_many([text]))[0]
