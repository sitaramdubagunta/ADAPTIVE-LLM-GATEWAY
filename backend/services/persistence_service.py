from sqlalchemy import text

from database import engine


def create_request(
    prompt: str,
    chat_id: int | None = None,
) -> int:

    with engine.begin() as conn:

        result = conn.execute(
            text(
                """
                INSERT INTO requests
                (
                    chat_id,
                    prompt
                )
                VALUES
                (
                    :chat_id,
                    :prompt
                )
                RETURNING id
                """
            ),
            {
                "chat_id": chat_id,
                "prompt": prompt,
            },
        )

        return result.scalar_one()


def create_response(
    request_id: int,
    provider_id: int,
    content: str,
    latency_ms: int,
    token_count: int | None = None,
    estimated_cost: float | None = None,
) -> int:

    with engine.begin() as conn:

        result = conn.execute(
            text(
                """
                INSERT INTO responses
                (
                    request_id,
                    provider_id,
                    content,
                    latency_ms,
                    token_count,
                    estimated_cost
                )
                VALUES
                (
                    :request_id,
                    :provider_id,
                    :content,
                    :latency_ms,
                    :token_count,
                    :estimated_cost
                )
                RETURNING id
                """
            ),
            {
                "request_id": request_id,
                "provider_id": provider_id,
                "content": content,
                "latency_ms": latency_ms,
                "token_count": token_count,
                "estimated_cost": estimated_cost,
            },
        )

        return result.scalar_one()