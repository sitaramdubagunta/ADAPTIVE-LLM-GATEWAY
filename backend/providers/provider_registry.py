from providers.gemini_provider import GeminiProvider
from providers.groq_provider import GroqProvider

PROVIDERS = {
    "gemini": GeminiProvider(),
    "groq": GroqProvider(),
}