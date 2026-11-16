class AIUnavailableError(Exception):
    """The AI provider (local Ollama or Hugging Face) could not be reached or refused the request."""


# Older name kept so existing imports keep working.
OllamaUnavailableError = AIUnavailableError


class DuplicateResourceError(Exception):
    pass
