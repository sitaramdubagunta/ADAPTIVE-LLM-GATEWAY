import asyncio
import json
import time
from collections.abc import AsyncGenerator
from providers.provider_registry import PROVIDERS
from services.persistence_service import (
    create_chat,
    create_request,
    create_response,
    update_chat_timestamp,
)
from services.router import choose_provider


PROVIDER_IDS = {
    "groq": 1,
    "gemini": 2,
}


class ChatService:
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
        candidates = [(provider_name, target_model)] + (
            [("gemini", "gemini-2.5-flash"), ("groq", "openai/gpt-oss-20b")]
            if provider_name == "gemini"
            else [("groq", "openai/gpt-oss-20b"), ("gemini", "gemini-2.5-flash")]
        )

        for candidate in candidates:
            if candidate not in seen:
                seen.add(candidate)
                yield candidate

    async def _stream_tokens(
        self, provider, message: str, model: str
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
        chat_id: int | None = None,
        stream: bool = False,
        current_user_id: int | None = None,
    ):
        if chat_id is None and current_user_id is not None:
            chat_id = create_chat(user_id=current_user_id, title=message[:80])

        request_id = create_request(prompt=message, chat_id=chat_id)
        route_config = choose_provider(message) or {"provider_name": "groq", "model_name": "openai/gpt-oss-20b"}
        provider_name, target_model = route_config["provider_name"], route_config["model_name"]

        if stream:
            async def token_stream():
                last_error = None

                for current_provider_name, current_model in self._route_candidates(provider_name, target_model):
                    provider = PROVIDERS[current_provider_name]
                    start_time = time.perf_counter()
                    parts = []

                    try:
                        async for token in self._stream_tokens(provider, message, current_model):
                            parts.append(token)

                            yield json.dumps({"type": "token", "content": token})

                        latency_ms = int((time.perf_counter() - start_time) * 1000)
                        create_response(request_id=request_id, provider_id=PROVIDER_IDS[current_provider_name], content="".join(parts), latency_ms=latency_ms)
                        if chat_id is not None:
                            update_chat_timestamp(chat_id)
                        yield json.dumps({"type": "meta", "provider": current_provider_name, "model": current_model, "latency_ms": latency_ms, "chat_id": chat_id})

                        return

                    except Exception as error:
                        last_error = error
                        if not self._is_quota_error(error):
                            raise

                if last_error is not None:
                    raise last_error

            return {"mode": "stream", "provider": provider_name, "model": target_model, "request_id": request_id, "generator": token_stream()}

        last_error = None

        for current_provider_name, current_model in self._route_candidates(provider_name, target_model):
            provider = PROVIDERS[current_provider_name]
            start_time = time.perf_counter()

            try:
                response = await asyncio.to_thread(provider.generate, message, current_model)
                latency_ms = int((time.perf_counter() - start_time) * 1000)
                create_response(request_id=request_id, provider_id=PROVIDER_IDS[current_provider_name], content=response, latency_ms=latency_ms)
                if chat_id is not None:
                    update_chat_timestamp(chat_id)
                return {"mode": "response", "provider": current_provider_name, "model": current_model, "latency_ms": latency_ms, "response": response, "chat_id": chat_id}

            except Exception as error:
                last_error = error
                if not self._is_quota_error(error):
                    raise

        if last_error is not None:
            raise last_error


chat_service = ChatService()