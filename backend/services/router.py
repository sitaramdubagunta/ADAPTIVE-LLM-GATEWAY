import json
import re

from sqlalchemy import text

from database import engine
from services.embedding_service import get_embedding


CODE_GUARD = re.compile(
    r"(?is)(?=.*\b(def|import|function|const|return|fn)\b)|(?=.*\{\})"
)

MATH_GUARD = re.compile(
    r"(?is)(?=.*[∫√])|(?=.*\b(matrix|calculus)\b)|(?=.*[=+\-*/^])"
)

GENERAL_QA_CATEGORY = "general_qa"


def _load_route_config(category: str) -> dict[str, str] | None:

    with engine.connect() as conn:

        result = conn.execute(
            text(
                """
                SELECT example_prompt
                FROM route_prototypes
                WHERE category = :category
                ORDER BY id
                LIMIT 1
                """
            ),
            {
                "category": category,
            }
        )

        row = result.fetchone()

    if not row or not row.example_prompt:
        return None

    try:
        config = json.loads(row.example_prompt)
    except json.JSONDecodeError:
        return None

    provider_name = config.get("provider_name")
    model_name = config.get("model_name")

    if not provider_name or not model_name:
        return None

    return {
        "provider_name": provider_name,
        "model_name": model_name,
    }


def choose_provider(prompt: str) -> dict[str, str]:

    if CODE_GUARD.search(prompt):
        return _load_route_config("coding") or _load_route_config(GENERAL_QA_CATEGORY)

    if MATH_GUARD.search(prompt):
        return _load_route_config("math") or _load_route_config(GENERAL_QA_CATEGORY)

    embedding = get_embedding(prompt)

    with engine.connect() as conn:

        result = conn.execute(
            text(
                """
                SELECT rp.example_prompt,
                       p.name AS provider_name,
                       rp.embedding <=> CAST(:embedding AS vector) AS distance
                FROM route_prototypes rp
                JOIN providers p
                    ON p.id = rp.provider_id
                ORDER BY
                    distance
                LIMIT 1
                """
            ),
            {
                "embedding": embedding,
            }
        )

        row = result.fetchone()

    if not row:
        return _load_route_config(GENERAL_QA_CATEGORY)

    if row.distance is None or row.distance > 0.65:
        return _load_route_config(GENERAL_QA_CATEGORY)

    try:
        config = json.loads(row.example_prompt)
    except json.JSONDecodeError:
        return _load_route_config(GENERAL_QA_CATEGORY)

    provider_name = config.get("provider_name") or row.provider_name
    model_name = config.get("model_name")

    if not provider_name or not model_name:
        return _load_route_config(GENERAL_QA_CATEGORY)

    return {
        "provider_name": provider_name,
        "model_name": model_name,
    }