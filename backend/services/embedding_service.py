from sentence_transformers import SentenceTransformer

model = SentenceTransformer(
    "all-MiniLM-L6-v2"
)
print("Embedding model loaded successfully.")

def get_embedding(text: str) -> list[float]:
    return model.encode(
        text,
        normalize_embeddings=True
    ).tolist()