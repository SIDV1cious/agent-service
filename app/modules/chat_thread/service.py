from sqlalchemy.ext.asyncio import AsyncSession
from .repository import ChatThreadRepository
from .models import ChatThread
from uuid import UUID
from app.modules.chat_thread.exceptions import ChatThreadNotFoundError

class ChatThreadService:

    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = ChatThreadRepository(session)

    async def add(self, user_id: int , title: str):
        # 1.用上下文管理开启事务，运行完成，自动commit，出现异常，自动rollback
        async with self.session.begin():
            # 2.创建对象，对象 映射 到数据库 一条数据
            chat_thread = ChatThread(user_id = user_id, title = title)
            # 3.调用Repository中的方法新增对象，也就是插入一条数据
            await self.repository.add(chat_thread)
            # 4.返回前端需要的数据
            return chat_thread

    async def list_by_user(self, user_id: int):
        # 没有额外业务，直接调用对象里面的方法就可以了
        return await self.repository.list_by_user(user_id)



    async def rename(
            self,
            thread_id: UUID,
            user_id: int,
            title: str
    ) -> ChatThread:
        async with self.session.begin():
            # 1.根据thread_id和user_id查询，判断是否匹配
            thread = await self.repository.find_owned(thread_id, user_id)
            if thread is None:
                # 将异常信息返回调用处，异常信息上报
                raise ChatThreadNotFoundError

            # 2.直接修改字段，只会修改 Python 内存里的 thread 对象的 title 属性，不会让 thread内部的updated_at 自动改变。
            thread.title = title

            # 3.提交数据到数据库，此时因为数据变更，数据库字段的updated_at会变更，与thread对象内的updated_at不再一致
            await self.session.flush()

            # 4.数据库内updated_at字段随着更新已经被修改了，我们要拿到最新的值
            await self.session.refresh(thread)
            #flush() 是把内存里的修改同步到数据库，refresh() 是把数据库里的最新数据重新同步回 Python 对象。
        return thread

    async def delete(
            self,
            thread_id: UUID,
            user_id: int,
    ) -> None:
        async with self.session.begin():
            thread = await self.repository.find_owned(thread_id, user_id)
            if thread is None:
                raise ChatThreadNotFoundError

            await self.repository.delete(thread)