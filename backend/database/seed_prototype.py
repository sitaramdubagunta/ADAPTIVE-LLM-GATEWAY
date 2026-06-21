from pathlib import Path
import sys

from sqlalchemy import text

sys.path.append(str(Path(__file__).resolve().parents[1]))

from database import engine
from services.embedding_service import get_embedding


PROTOTYPES = {
    "general_qa": [
        "What is TCP?",
        "Explain DNS",
        "What is Linux?",
        "How does HTTP work?",
        "What is a database?"
    ],

    "coding": [
        "Reverse a linked list",
        "Two Sum problem",
        "Implement LRU cache",
        "Binary search explanation",
        "Kadane algorithm"
    ],

    "system_design": [
        "Design Instagram",
        "Design Netflix",
        "Design WhatsApp",
        "Design Uber",
        "Design YouTube"
    ],

    "math": [
        "Solve x squared plus five x plus six",
        "Explain derivatives",
        "What is calculus?",
        "Integrate x squared",
        "Find the determinant of a matrix"
    ],

    "creative": [
        "Write a fantasy story",
        "Write a poem",
        "Create a sci fi world",
        "Write a dialogue",
        "Generate a character backstory"
    ]
}


CATEGORY_PROVIDER = {
    "general_qa": "groq",
    "coding": "groq",
    "math": "groq",
    "system_design": "gemini",
    "creative": "gemini"
}


with engine.begin() as conn:

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
            CATEGORY_PROVIDER[category]
        ]

        for prompt in prompts:

            embedding = get_embedding(prompt)

            vector_string = (
                "[" +
                ",".join(
                    str(x)
                    for x in embedding
                ) +
                "]"
            )

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
                    "prompt": prompt,
                    "embedding": vector_string,
                    "provider_id": provider_id
                }
            )

print("Prototype routes seeded successfully.")