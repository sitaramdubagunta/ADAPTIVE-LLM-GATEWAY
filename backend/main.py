from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from database.models import User
from routes.auth import router as auth_router
from services.auth_service import get_current_user
from services.chat_service import chat_service
from services.persistence_service import (
    get_user_chats,
    get_chat_messages,
    verify_chat_owner,
)

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
    chat_id: int | None = None


@app.get("/")
def root():
    return {"message": "Hello from FastAPI"}


@app.get("/v1/chats")
def list_chats(current_user: User = Depends(get_current_user)):
    return get_user_chats(user_id=current_user.id)


@app.get("/v1/chats/{chat_id}/messages")
def list_messages(
    chat_id: int,
    current_user: User = Depends(get_current_user),
):
    if not verify_chat_owner(chat_id, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this chat session.",
        )
    return get_chat_messages(chat_id)


@app.post("/v1/chat")
async def chat_v1(
    req: ChatRequest,
    current_user: User = Depends(get_current_user),
):
    if req.chat_id is not None:
        if not verify_chat_owner(req.chat_id, current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied to this chat session.",
            )

    result = await chat_service.handle_message(
        req.message,
        chat_id=req.chat_id,
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



