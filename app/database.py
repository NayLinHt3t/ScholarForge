import os

from google.cloud import firestore

_client: firestore.Client | None = None


def get_db() -> firestore.Client:
    global _client
    if _client is None:
        project = os.environ["GOOGLE_CLOUD_PROJECT"]
        _client = firestore.Client(project=project)
    return _client
