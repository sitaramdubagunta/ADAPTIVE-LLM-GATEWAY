from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from database.models import User
from routes.auth import router as auth_router
from services.auth_service import get_current_user
from services.chat_service import chat_service

app = FastAPI()
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:5174"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return {"message": "Hello from FastAPI"}


@app.post("/v1/chat")
async def chat_v1(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    result = await chat_service.handle_message(
        req.message,
        stream=True,
        current_user_id=current_user.id,
    )

    async def sse_stream():
        async for event in result["generator"]:
            yield f"data: {event}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(
        sse_stream(),
        media_type="text/event-stream",
    )


