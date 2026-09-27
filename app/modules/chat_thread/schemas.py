from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field, field_validator
from typing import Any, Literal
from pydantic import BaseModel

class ChatThreadCreate(BaseModel):
    """创建会话请求体类"""

    title: str = Field(default="新会话", min_length=1, max_length=200)

    @field_validator("title", mode="before")
    @classmethod
    # cls 代表当前模型类 ChatThreadCreate 本身。
    # 因为字段校验发生在模型对象正式创建之前，此时还没有具体实例 self，
    # 所以这里使用类方法，通过 cls 接收当前类。
    def normalize_title(cls, value: str) -> str:
        return value.strip()

class ChatThreadResponse(BaseModel):
    """会话响应"""

    id: UUID
    title: str
    created_at: datetime
    updated_at: datetime

# 每一条消息对应的模型
class ChatMessageResponse(BaseModel):
    role:Literal["user", "assistant"]
    content:str

# 存储所有消息的模型
class ChatHistoryResponse(BaseModel):
    thread_id:UUID
    messages:list[ChatMessageResponse]