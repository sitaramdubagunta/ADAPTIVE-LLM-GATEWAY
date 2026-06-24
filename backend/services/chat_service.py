import asyncio
import time
from collections.abc import AsyncGenerator

from database.tasks import process_heavy_task
from providers.provider_registry import PROVIDERS
from services.persistence_service import (
    create_chat,
    create_request,
    create_response,
)
from services.router import choose_provider


PROVIDER_IDS = {
    "groq": 1,
    "gemini": 2,
}


HEAVY_MODEL_MARKERS = (
    "whisper",
    "scout",
    "vision",
)


class ChatService:
    @staticmethod
    def _is_heavy_route(target_model: str) -> bool:
        return any(marker in target_model for marker in HEAVY_MODEL_MARKERS)

    @staticmethod
    def _is_quota_error(error: Exception) -> bool:
        error_text = str(error).lower()
        return (
            "quota" in error_text
            or "resource_exhausted" in error_text
            or "unavailable" in error_text
            or "too many requests" in error_text
            or "429" in error_text
            or "503" in error_text
        )

    def _route_candidates(self, provider_name: str, target_model: str):
        seen = set()

        def add_candidate(name: str, model: str):
            key = (name, model)
            if key not in seen:
                seen.add(key)
                yield key

        yield from add_candidate(provider_name, target_model)

        if provider_name == "gemini":
            yield from add_candidate("gemini", "gemini-2.5-flash")
            yield from add_candidate("groq", "openai/gpt-oss-20b")
        else:
            yield from add_candidate("groq", "openai/gpt-oss-20b")
            yield from add_candidate("gemini", "gemini-2.5-flash")

    async def _stream_tokens(
        self,
        provider,
        message: str,
        model: str,
    ) -> AsyncGenerator[str, None]:
        stream_method = getattr(provider, "generate_stream", None)

        if callable(stream_method):
            async for token in stream_method(message, model=model):
                yield token
            return

        response = await asyncio.to_thread(provider.generate, message, model)

        if response:
            yield response

    async def handle_message(
        self,
        message: str,
        stream: bool = False,
        current_user_id: int | None = None,
    ):
        chat_id = (
            create_chat(
                user_id=current_user_id,
                title=message[:80],
            )
            if current_user_id is not None
            else None
        )

        request_id = create_request(
            prompt=message,
            chat_id=chat_id,
        )

        route_config = choose_provider(message) or {
            "provider_name": "groq",
            "model_name": "openai/gpt-oss-20b",
        }

        provider_name = route_config["provider_name"]
        target_model = route_config["model_name"]

        if self._is_heavy_route(target_model):
            task = process_heavy_task.delay(
                message,
                {
                    **route_config,
                    "request_id": request_id,
                },
            )

            return {
                "mode": "processing",
                "status": "processing",
                "task_id": task.id,
                "request_id": request_id,
                "provider": provider_name,
                "model": target_model,
            }

        if stream:

            async def token_stream():
                last_error = None

                for current_provider_name, current_model in self._route_candidates(
                    provider_name,
                    target_model,
                ):
                    provider = PROVIDERS[current_provider_name]
                    start_time = time.perf_counter()
                    parts = []

                    try:
                        async for token in self._stream_tokens(
                            provider,
                            message,
                            current_model,
                        ):
                            parts.append(token)
                            yield token

                        latency_ms = int((time.perf_counter() - start_time) * 1000)

                        create_response(
                            request_id=request_id,
                            provider_id=PROVIDER_IDS[current_provider_name],
                            content="".join(parts),
                            latency_ms=latency_ms,
                        )
                        return

                    except Exception as error:
                        last_error = error
                        if not self._is_quota_error(error):
                            raise

                if last_error is not None:
                    raise last_error

            return {
                "mode": "stream",
                "provider": provider_name,
                "model": target_model,
                "request_id": request_id,
                "generator": token_stream(),
            }

        last_error = None

        for current_provider_name, current_model in self._route_candidates(
            provider_name,
            target_model,
        ):
            provider = PROVIDERS[current_provider_name]
            start_time = time.perf_counter()

            try:
                response = await asyncio.to_thread(
                    provider.generate,
                    message,
                    current_model,
                )

                latency_ms = int((time.perf_counter() - start_time) * 1000)

                create_response(
                    request_id=request_id,
                    provider_id=PROVIDER_IDS[current_provider_name],
                    content=response,
                    latency_ms=latency_ms,
                )

                return {
                    "mode": "response",
                    "provider": current_provider_name,
                    "model": current_model,
                    "latency_ms": latency_ms,
                    "response": response,
                }

            except Exception as error:
                last_error = error
                if not self._is_quota_error(error):
                    raise

        if last_error is not None:
            raise last_error


chat_service = ChatService()


async def generate_response(message: str):
    return await chat_service.handle_message(message, stream=False)