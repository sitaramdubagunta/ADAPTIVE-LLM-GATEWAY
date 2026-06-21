from sqlalchemy import text

from database import engine
from services.embedding_service import get_embedding


def choose_provider(prompt: str) -> str:

    embedding = get_embedding(prompt)

    vector_string = (
        "[" +
        ",".join(str(x) for x in embedding) +
        "]"
    )

    with engine.connect() as conn:

        result = conn.execute(
            text(
                """
                SELECT p.name
                FROM route_prototypes rp
                JOIN providers p
                    ON p.id = rp.provider_id
                ORDER BY
                    rp.embedding <=> CAST(:embedding AS vector)
                LIMIT 1
                """
            ),
            {
                "embedding": vector_string
            }
        )

        row = result.fetchone()

    return row.name if row else "groq"