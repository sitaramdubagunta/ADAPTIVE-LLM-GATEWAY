from fastapi import Depends, FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import BaseModel

from database.models import User
from routes.auth import router as auth_router
from services.auth_service import get_current_user
from services.chat_service import chat_service, generate_response

app = FastAPI()
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


@app.get("/")
def root():
    return {"message": "Hello from FastAPI"}


@app.post("/chat")
async def chat(req: ChatRequest):
    return await generate_response(req.message)


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

    if result["mode"] == "processing":
        return JSONResponse(
            status_code=202,
            content={
                "status": "processing",
                "task_id": result["task_id"],
                "provider": result["provider"],
                "model": result["model"],
            },
        )

    async def sse_stream():
        async for token in result["generator"]:
            yield f"data: {token}\n\n"

        yield "data: [DONE]\n\n"

    return StreamingResponse(
        sse_stream(),
        media_type="text/event-stream",
    )


async def _accept_upload(kind: str, file: UploadFile):
    content = await file.read()

    return {
        "status": "received",
        "kind": kind,
        "filename": file.filename,
        "content_type": file.content_type,
        "size_bytes": len(content),
    }


@app.post("/v1/audio")
async def audio_upload(file: UploadFile = File(...)):
    return await _accept_upload("audio", file)


@app.post("/v1/image")
async def image_upload(file: UploadFile = File(...)):
    return await _accept_upload("image", file)