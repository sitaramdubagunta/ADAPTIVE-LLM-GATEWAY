import time

from providers.provider_registry import PROVIDERS
from services.router import choose_provider
from services.persistence_service import (
    create_request,
    create_response,
)

PROVIDER_IDS = {
    "groq": 1,
    "gemini": 2,
}


def generate_response(message: str):

    request_id = create_request(
        prompt=message
    )

    provider_name = choose_provider(
        message
    )

    provider = PROVIDERS[
        provider_name
    ]

    start_time = time.perf_counter()

    try:

        response = provider.generate(
            message
        )

    except Exception as e:

        print(
            f"{provider_name} failed: {e}"
        )

        fallback_provider = (
            "groq"
            if provider_name == "gemini"
            else "gemini"
        )

        print(
            f"Falling back to {fallback_provider}"
        )

        provider = PROVIDERS[
            fallback_provider
        ]

        response = provider.generate(
            message
        )

        provider_name = fallback_provider

    latency_ms = int(
        (time.perf_counter() - start_time)
        * 1000
    )

    create_response(
        request_id=request_id,
        provider_id=PROVIDER_IDS[
            provider_name
        ],
        content=response,
        latency_ms=latency_ms,
    )

    return {
        "provider": provider_name,
        "latency_ms": latency_ms,
        "response": response,
    }