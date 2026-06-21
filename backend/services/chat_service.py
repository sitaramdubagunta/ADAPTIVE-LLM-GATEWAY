from providers.provider_registry import PROVIDERS
from services.router import choose_provider


def generate_response(message: str):
    provider_name = choose_provider(message)
    provider = PROVIDERS[provider_name]
    response = provider.generate(message)

    return {
        "provider": provider_name,
        "response": response,
    }