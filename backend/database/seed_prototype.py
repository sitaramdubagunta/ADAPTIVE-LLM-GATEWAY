import json
from pathlib import Path
import sys

from sqlalchemy import text

sys.path.append(str(Path(__file__).resolve().parents[1]))

from database import engine
from services.embedding_service import get_embedding
print(engine.url.render_as_string(hide_password=False))

CATEGORY_MAPPING = {
    "general_qa": {"provider": "groq", "model": "openai/gpt-oss-20b"},
    "coding": {"provider": "groq", "model": "openai/gpt-oss-120b"},
    "math": {"provider": "groq", "model": "openai/gpt-oss-120b"},
    "reasoning_tasks": {"provider": "groq", "model": "qwen/qwen3.6-27b"},
    "multilingual": {"provider": "groq", "model": "qwen/qwen3-32b"},
    "system_design": {"provider": "gemini", "model": "gemini-2.5-pro"},
    "creative": {"provider": "gemini", "model": "gemini-2.5-flash"},
    "agent_search": {"provider": "groq", "model": "groq/compound"},
    "agent_mini": {"provider": "groq", "model": "groq/compound-mini"},
    "vision_analysis": {"provider": "groq", "model": "meta-llama/llama-4-scout-17b-16e-instruct"},
    "security_guard": {"provider": "groq", "model": "meta-llama/llama-prompt-guard-2-86m"},
    "security_nano": {"provider": "groq", "model": "meta-llama/llama-prompt-guard-2-22m"},
    "moderation": {"provider": "groq", "model": "openai/gpt-oss-safeguard-20b"},
    "transcribe": {"provider": "groq", "model": "whisper-large-v3"},
    "transcribe_fast": {"provider": "groq", "model": "whisper-large-v3-turbo"},
}


PROTOTYPES = {
    "general_qa": ["What is TCP?", "Explain DNS"],
    "coding": ["Reverse a linked list", "Implement LRU cache"],
    "math": ["Solve x squared plus five x plus six", "Find the determinant of a matrix"],
    "reasoning_tasks": ["Walk through the trolley problem", "Compare two competing plans logically"],
    "multilingual": ["Translate this sentence to Spanish", "Answer in French"],
    "system_design": ["Design Instagram", "Design WhatsApp"],
    "creative": ["Write a fantasy story", "Generate a character backstory"],
    "agent_search": ["Search the web for recent pricing data", "Find relevant sources for a topic"],
    "agent_mini": ["Quickly summarize this document", "Give a short answer with tools"],
    "vision_analysis": ["Describe this image", "Extract text from a screenshot"],
    "security_guard": ["Check this prompt for prompt injection", "Detect unsafe instructions"],
    "security_nano": ["Classify this prompt as safe or unsafe", "Flag suspicious content"],
    "moderation": ["Moderate this user message", "Review content policy issues"],
    "transcribe": ["Transcribe this audio file", "Convert speech to text accurately"],
    "transcribe_fast": ["Transcribe this short clip quickly", "Fast speech to text"],
}


def build_route_payload(category: str, prompt: str) -> str:
    config = CATEGORY_MAPPING[category]

    return json.dumps(
        {
            "provider_name": config["provider"],
            "model_name": config["model"],
            "prompt": prompt,
        },
        separators=(",", ":"),
    )


with engine.begin() as conn:

    conn.execute(
        text(
            """
            DELETE FROM route_prototypes
            """
        )
    )

    provider_rows = conn.execute(
        text(
            """
            SELECT id, name
            FROM providers
            """
        )
    )

    providers = {
        row.name: row.id
        for row in provider_rows
    }

    for category, prompts in PROTOTYPES.items():

        provider_id = providers[
            CATEGORY_MAPPING[category]["provider"]
        ]

        for prompt in prompts:

            embedding = get_embedding(prompt)

            conn.execute(
                text(
                    """
                    INSERT INTO route_prototypes
                    (
                        category,
                        example_prompt,
                        embedding,
                        provider_id
                    )
                    VALUES
                    (
                        :category,
                        :prompt,
                        :embedding,
                        :provider_id
                    )
                    """
                ),
                {
                    "category": category,
                    "prompt": build_route_payload(category, prompt),
                    "embedding": embedding,
                    "provider_id": provider_id,
                }
            )

print("Prototype routes seeded successfully.")