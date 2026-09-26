from sqlalchemy.ext.asyncio import AsyncSession
from .models import ChatThread
from sqlalchemy import select
from uuid import UUID

class ChatThreadRepository:

    def __init__(self, session:AsyncSession):
        self.session = session

    async def add(self, chat_thread: ChatThread):
        # 添加会话
        self.session.add(chat_thread)

    async def list_by_user(self, user_id: int) -> list[ChatThread]:
        # 1. 准备 SQL 语句
        sql = (
            select(ChatThread)
            .where(ChatThread.user_id == user_id)
            .order_by(
                ChatThread.updated_at.desc(),
                ChatThread.created_at.desc(),
            )
        )
        # 2. 执行 SQL 语句
        result = await self.session.scalars(sql)
        # 3. 解析执行结果,将解析出的ChatThread列表返回
        return list(result.all())

    async def find_owned(
            self,
            thread_id: UUID,
            user_id: int,
    ) -> ChatThread | None:
        # 1.准备SQL语句
        sql = select(ChatThread).where(ChatThread.id == thread_id, ChatThread.user_id == user_id)
        # 2.执行SQL语句
        execute_result = await self.session.execute(sql)
        # 3.解析执行结果
        return execute_result.scalars().one_or_none() #查找到的会话至多为1条，会话id或用户id对不上则结果为0条

    async def delete(self, thread: ChatThread) -> None:
        await self.session.delete(thread)
        # 在Repository层没有进行提交操作，目的就是在Service层统一进行事务的管理