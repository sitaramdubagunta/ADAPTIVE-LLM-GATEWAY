import asyncio
import os

from dotenv import load_dotenv
from groq import Groq

try:
    from groq import AsyncGroq
except ImportError:
    AsyncGroq = None

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
async_client = (
    AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
    if AsyncGroq is not None
    else None
)


class GroqProvider:
    def generate(self, message: str, model: str = None):
        response = client.chat.completions.create(
            model=model or "openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": message,
                }
            ],
        )

        return response.choices[0].message.content

    async def generate_stream(self, message: str, model: str = None):
        if async_client is None:
            response = await asyncio.to_thread(
                self.generate,
                message,
                model,
            )

            if response:
                yield response
            return

        stream = await async_client.chat.completions.create(
            model=model or "openai/gpt-oss-20b",
            messages=[
                {
                    "role": "user",
                    "content": message,
                }
            ],
            stream=True,
        )

        async for chunk in stream:
            token = getattr(
                getattr(
                    chunk.choices[0],
                    "delta",
                    None,
                ),
                "content",
                None,
            )

            if token:
                yield token