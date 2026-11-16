import os

# ── AI provider ──────────────────────────────────────────────────────────────
# Chat / text generation:
#   "ollama"      → models run locally on this machine (default, development)
#   "groq"        → Groq free tier (hosted, $0)
#   "huggingface" → Hugging Face Inference Providers (hosted, paid credits)
AI_PROVIDER: str = os.environ.get("AI_PROVIDER", "ollama").strip().lower()
# Embeddings (semantic search). Default follows AI_PROVIDER; Groq has no embeddings,
# so with "groq" they run on the server itself ("local", FastEmbed).
EMBED_PROVIDER: str = os.environ.get(
    "EMBED_PROVIDER", {"groq": "local"}.get(AI_PROVIDER, AI_PROVIDER)
).strip().lower()

GROQ_API_KEY: str = os.environ.get("GROQ_API_KEY", "")
GROQ_BASE_URL: str = os.environ.get("GROQ_BASE_URL", "https://api.groq.com/openai/v1")
GROQ_MODEL: str = os.environ.get("GROQ_MODEL", "openai/gpt-oss-20b")

LOCAL_EMBED_MODEL: str = os.environ.get("LOCAL_EMBED_MODEL", "BAAI/bge-small-en-v1.5")
LOCAL_EMBED_CACHE: str | None = os.environ.get("LOCAL_EMBED_CACHE") or None

OLLAMA_BASE_URL: str = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
EMBED_MODEL: str = "nomic-embed-text"
GENERATE_MODEL: str = "llama3.2:3b"

HF_TOKEN: str = os.environ.get("HF_TOKEN", "")
HF_BASE_URL: str = os.environ.get("HF_BASE_URL", "https://router.huggingface.co")
HF_CHAT_MODEL: str = os.environ.get("HF_CHAT_MODEL", "openai/gpt-oss-20b")
HF_EMBED_MODEL: str = os.environ.get("HF_EMBED_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

SEMANTIC_SCHOLAR_API_KEY: str = os.environ.get("SEMANTIC_SCHOLAR_API_KEY", "")

# ── Hosting / monitoring ─────────────────────────────────────────────────────
# Admin portal (/admin) — separate from student accounts.
# ADMIN_PASSWORD_HASH is a bcrypt hash made with:  python -m app.tools.admin_password
ADMIN_USERNAME: str = os.environ.get("ADMIN_USERNAME", "").strip()
ADMIN_PASSWORD_HASH: str = os.environ.get("ADMIN_PASSWORD_HASH", "").strip()
ADMIN_SESSION_HOURS: int = int(os.environ.get("ADMIN_SESSION_HOURS", "8"))
# Set to "true" when served over HTTPS (e.g. Cloud Run) so the session cookie is Secure.
COOKIE_SECURE: bool = os.environ.get("COOKIE_SECURE", "false").lower() == "true"
# Access log (Computer Crime Act §26): keep at least 90 days.
ACCESS_LOG_ENABLED: bool = os.environ.get("ACCESS_LOG_ENABLED", "true").lower() == "true"
ACCESS_LOG_RETENTION_DAYS: int = 91
# Timezone used for the "busiest hours" chart on the admin dashboard.
DASHBOARD_TZ: str = os.environ.get("DASHBOARD_TZ", "Asia/Bangkok")

# BL-43: single named constant — change only here to adjust the low-confidence cut-off
SEARCH_LOW_CONFIDENCE_THRESHOLD: float = 0.3

SEARCH_MAX_PER_SOURCE: int = 15
SEARCH_TOP_K: int = 10
