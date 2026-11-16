"""Groq chat client (free tier, OpenAI-compatible). Used for the hosted version.

POST {GROQ_BASE_URL}/chat/completions   Authorization: Bearer GROQ_API_KEY
Groq has no embeddings API — embeddings run locally (app/clients/local_embed.py).
"""
import logging

import httpx

from app import config
from app.exceptions import AIUnavailableError

log = logging.getLogger(__name__)

_TIMEOUT = httpx.Timeout(60.0, connect=10.0)


async def is_alive() -> bool:
    """Cheap check (no network call): is a key configured?"""
    return bool(config.GROQ_API_KEY)


async def generate(prompt: str) -> str:
    if not config.GROQ_API_KEY:
        raise AIUnavailableError("GROQ_API_KEY is not set")
    payload = {
        "model": config.GROQ_MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_completion_tokens": 900,
        "temperature": 0.3,
    }
    if config.GROQ_MODEL.startswith("openai/gpt-oss"):
        payload["reasoning_effort"] = "low"      # faster, fewer tokens against the free limit
    try:
        async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
            r = await client.post(
                f"{config.GROQ_BASE_URL}/chat/completions",
                json=payload,
                headers={"Authorization": f"Bearer {config.GROQ_API_KEY}", "Content-Type": "application/json"},
            )
    except httpx.HTTPError as e:
        raise AIUnavailableError(f"Groq unreachable: {type(e).__name__}") from e
    if r.status_code >= 400:
        # 429 = free-tier rate limit reached. Never log the key.
        log.warning("groq.chat.error status=%s body=%s", r.status_code, r.text[:200])
        raise AIUnavailableError(f"Groq chat failed with HTTP {r.status_code}")
    try:
        return r.json()["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, ValueError) as e:
        raise AIUnavailableError("Unexpected response from Groq") from e
