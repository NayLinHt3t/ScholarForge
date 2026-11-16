"""Embeddings computed on the app server itself with FastEmbed (ONNX, CPU only).

Free and private: search text and abstracts used for matching never leave the server.
The model files are downloaded once when the Docker image is built (see Dockerfile),
so a new Cloud Run instance does not download anything at start-up.
"""
import asyncio
import logging
import threading

from app import config
from app.exceptions import AIUnavailableError

log = logging.getLogger(__name__)

_model = None
_lock = threading.Lock()


def _get_model():
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                try:
                    from fastembed import TextEmbedding
                except ImportError as e:  # not installed (e.g. local dev without requirements-cloud.txt)
                    raise AIUnavailableError("fastembed is not installed") from e
                try:
                    _model = TextEmbedding(model_name=config.LOCAL_EMBED_MODEL, cache_dir=config.LOCAL_EMBED_CACHE,
                                           threads=config.LOCAL_EMBED_THREADS)
                except Exception as e:  # noqa: BLE001 — model missing / cannot download
                    log.warning("local_embed.load_failed error=%s", e)
                    raise AIUnavailableError("Local embedding model could not be loaded") from e
    return _model


def _embed_sync(texts: list[str]) -> list[list[float]]:
    model = _get_model()
    return [[float(x) for x in vec] for vec in model.embed(texts, batch_size=16)]


async def is_alive() -> bool:
    try:
        import fastembed  # noqa: F401
        return True
    except ImportError:
        return False


async def embed_many(texts: list[str]) -> list[list[float]]:
    if not texts:
        return []
    # ONNX inference is CPU work — run it off the event loop.
    return await asyncio.to_thread(_embed_sync, texts)
