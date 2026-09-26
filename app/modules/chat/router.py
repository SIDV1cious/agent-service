from typing import Annotated
from fastapi import APIRouter, Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from app.infra.database import get_session
from app.modules.chat.schemas import ChatRequest
from app.modules.chat.service import ChatService

router = APIRouter(prefix="/api/v1/chat", tags=["聊天业务"])

async def get_service(
        request:Request,
        session:AsyncSession = Depends(get_session),
):
    return ChatService(session, request.app.state.agent)

@router.post("", summary="与AI交互聊天")
async def chat_stream(
    chat_request:ChatRequest,
    user_id:Annotated[int, Header(alias="x-user-id")],
    service:ChatService = Depends(get_service)
):
    return await service.chat_stream(chat_request.thread_id, user_id, chat_request.message)