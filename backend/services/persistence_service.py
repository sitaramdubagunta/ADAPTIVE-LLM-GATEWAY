from sqlalchemy import text

from database import engine


def _insert_returning_id(query: str, params: dict) -> int:
    with engine.begin() as conn:
        result = conn.execute(text(query), params)
        return result.scalar_one()


def create_chat(
    user_id: int,
    title: str | None = None,
) -> int:
    return _insert_returning_id(
        """
        INSERT INTO chats
        (
            user_id,
            title
        )
        VALUES
        (
            :user_id,
            :title
        )
        RETURNING id
        """,
        {
            "user_id": user_id,
            "title": title,
        },
    )


def create_request(
    prompt: str,
    chat_id: int | None = None,
) -> int:
    return _insert_returning_id(
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
        """,
        {
            "chat_id": chat_id,
            "prompt": prompt,
        },
    )


def create_response(
    request_id: int,
    provider_id: int,
    content: str,
    latency_ms: int,
    token_count: int | None = None,
    estimated_cost: float | None = None,
) -> int:
    return _insert_returning_id(
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
        """,
        {
            "request_id": request_id,
            "provider_id": provider_id,
            "content": content,
            "latency_ms": latency_ms,
            "token_count": token_count,
            "estimated_cost": estimated_cost,
        },
    )


def get_user_chats(user_id: int) -> list[dict]:
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT id, title, created_at, updated_at
                FROM chats
                WHERE user_id = :user_id
                ORDER BY updated_at DESC
                """
            ),
            {"user_id": user_id},
        )

        return [
            {
                "id": row.id,
                "title": row.title,
                "created_at": row.created_at,
                "updated_at": row.updated_at,
            }
            for row in result
        ]


def get_chat_messages(chat_id: int) -> list[dict]:
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT
                    r.id AS request_id,
                    r.prompt,
                    r.created_at AS request_created_at,
                    resp.id AS response_id,
                    resp.content AS response_content,
                    resp.latency_ms,
                    p.name AS provider_name
                FROM requests r
                LEFT JOIN responses resp ON resp.request_id = r.id
                LEFT JOIN providers p ON p.id = resp.provider_id
                WHERE r.chat_id = :chat_id
                ORDER BY r.created_at ASC, resp.id ASC
                """
            ),
            {"chat_id": chat_id},
        )

        messages = []

        for row in result:
            messages.append(
                {
                    "id": int(row.request_id) * 2,
                    "role": "user",
                    "content": row.prompt,
                }
            )

            if row.response_id is not None:
                messages.append(
                    {
                        "id": int(row.response_id) * 2 + 1,
                        "role": "assistant",
                        "content": row.response_content,
                        "metadata": {
                            "provider": row.provider_name,
                            "model": "routed",
                            "latency_ms": row.latency_ms,
                        },
                    }
                )

        return messages


def update_chat_timestamp(chat_id: int):
    with engine.begin() as conn:
        conn.execute(
            text(
                """
                UPDATE chats
                SET updated_at = NOW()
                WHERE id = :chat_id
                """
            ),
            {"chat_id": chat_id},
        )


def verify_chat_owner(chat_id: int, user_id: int) -> bool:
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT 1
                FROM chats
                WHERE id = :chat_id
                  AND user_id = :user_id
                """
            ),
            {
                "chat_id": chat_id,
                "user_id": user_id,
            },
        )

        return result.fetchone() is not None