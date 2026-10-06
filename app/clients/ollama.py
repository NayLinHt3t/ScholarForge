import httpx

from app.config import EMBED_MODEL, GENERATE_MODEL, OLLAMA_BASE_URL
from app.exceptions import OllamaUnavailableError

_CONNECT_ERRORS = (httpx.ConnectError, httpx.ConnectTimeout)


async def is_alive() -> bool:
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{OLLAMA_BASE_URL}/api/tags")
            return r.status_code == 200
    except Exception:
        return False


async def embed(text: str) -> list[float]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            r = await client.post(
                f"{OLLAMA_BASE_URL}/api/embeddings",
                json={"model": EMBED_MODEL, "prompt": text},
            )
            r.raise_for_status()
            return r.json()["embedding"]
        except _CONNECT_ERRORS:
            raise OllamaUnavailableError()


async def generate(prompt: str) -> str:
    async with httpx.AsyncClient(timeout=120.0) as client:
        try:
            r = await client.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json={"model": GENERATE_MODEL, "prompt": prompt, "stream": False},
            )
            r.raise_for_status()
            return r.json()["response"]
        except _CONNECT_ERRORS:
            raise OllamaUnavailableError()
