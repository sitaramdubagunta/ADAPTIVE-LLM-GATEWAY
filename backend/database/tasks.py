import asyncio
import os

import httpx
from celery import Celery

from providers.provider_registry import PROVIDERS
from services.persistence_service import create_request, create_response


celery_app = Celery(
    "llm_gateway",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
)


PROVIDER_IDS = {
    "groq": 1,
    "gemini": 2,
}


async def _run_heavy_workload(prompt: str, route_profile: dict) -> str:
    provider_name = route_profile["provider_name"]
    model_name = route_profile["model_name"]

    async with httpx.AsyncClient(timeout=120.0) as client:
        _ = client

    if "whisper" in model_name:
        return f"completed transcription job for {model_name}: {prompt}"

    provider = PROVIDERS.get(provider_name)
    if provider is not None and hasattr(provider, "generate"):
        return await asyncio.to_thread(
            provider.generate,
            prompt,
            model_name,
        )

    return f"completed background job for {provider_name}:{model_name}: {prompt}"


@celery_app.task(name="process_heavy_task")
def process_heavy_task(prompt: str, route_profile: dict):
    request_id = route_profile.get("request_id") or create_request(
        prompt=prompt,
        chat_id=route_profile.get("chat_id"),
    )

    response_text = asyncio.run(
        _run_heavy_workload(prompt, route_profile)
    )

    create_response(
        request_id=request_id,
        provider_id=PROVIDER_IDS[route_profile["provider_name"]],
        content=response_text,
        latency_ms=0,
    )

    return {
        "request_id": request_id,
        "provider": route_profile["provider_name"],
        "model": route_profile["model_name"],
    }