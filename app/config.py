import os

# ── AI provider ──────────────────────────────────────────────────────────────
# "ollama"      → models run locally on this machine (default, development)
# "huggingface" → Hugging Face Inference Providers (used when hosted)
AI_PROVIDER: str = os.environ.get("AI_PROVIDER", "ollama").strip().lower()

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
