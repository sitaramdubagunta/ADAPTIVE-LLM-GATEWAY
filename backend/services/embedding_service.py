import hashlib
import threading
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")
_cache = {}
_cache_lock = threading.Lock()


def get_embedding(text: str) -> list[float]:
    hasher = hashlib.sha256()
    hasher.update(text.encode("utf-8"))
    cache_key = hasher.hexdigest()

    with _cache_lock:
        if cache_key in _cache:
            return _cache[cache_key]

    embedding = model.encode(text, normalize_embeddings=True).tolist()

    with _cache_lock:
        _cache[cache_key] = embedding

    return embedding