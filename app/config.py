OLLAMA_BASE_URL: str = "http://localhost:11434"
EMBED_MODEL: str = "nomic-embed-text"
GENERATE_MODEL: str = "llama3.2:3b"

# BL-43: single named constant — change only here to adjust the low-confidence cut-off
SEARCH_LOW_CONFIDENCE_THRESHOLD: float = 0.3

SEARCH_MAX_PER_SOURCE: int = 15
SEARCH_TOP_K: int = 10
