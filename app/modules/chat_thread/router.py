from typing import Annotated
from fastapi import APIRouter, Depends, Header
from sqlalchemy.ext.asyncio import AsyncSession
from app.infra.database import get_session
from .schemas import *
from .service import ChatThreadService
from uuid import UUID

router = APIRouter(prefix = "/api/v1/chat-threads", tags=["会话管理"])

def get_service(session:AsyncSession = Depends(get_session)):
    return ChatThreadService(session)

@router.post("", response_model=ChatThreadResponse)
async def create_chat_thread(
    request: ChatThreadCreate,
    user_id: Annotated[int, Header(alias="x-user-id")],
    service:ChatThreadService = Depends(get_service),
):
    """创建会话"""
    return await service.add(user_id, request.title)

@router.get("", response_model=list[ChatThreadResponse])
async def list_chat_threads(
    user_id: Annotated[int, Header(alias="x-user-id")],
    service: ChatThreadService = Depends(get_service),
):
    # 调用Service中的方法，根据用户ID查询会话列表
    return await service.list_by_user(user_id)

@router.patch("/{thread_id}", response_model=ChatThreadResponse)
async def rename(
    thread_id: str,
    request: ChatThreadCreate,
    user_id: Annotated[int, Header(alias="x-user-id")],
    service: ChatThreadService = Depends(get_service),
):
    """重命名会话"""
    return await service.rename(thread_id, user_id, request.title)

from fastapi import Response, status


@router.delete(
    "/{thread_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_chat_thread(
    thread_id: UUID,
    user_id: Annotated[int, Header(alias="x-user-id")],
    service: ChatThreadService = Depends(get_service),
) -> Response:
    """删除指定会话"""

    await service.delete(thread_id, user_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
