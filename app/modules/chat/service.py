from uuid import UUID
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.chat_thread.exceptions import ChatThreadNotFoundError
from app.modules.chat_thread.repository import ChatThreadRepository

class ChatService:
    def __init__(self, session:AsyncSession, agent:CompiledStateGraph):
        self.repository = ChatThreadRepository(session)
        self.agent = agent

    async def chat_stream(self, thread_id:UUID, user_id:int, message:str):
        # 1.验证当前会话是不是属于当前登录的用户
        chat_thread = self.repository.find_owned(thread_id, user_id)
        if chat_thread is None:
            raise ChatThreadNotFoundError

        # 2.目标：通过智能体发送消息给大模型
        # 2.1 准备好消息列表
        Input = {
            "messages":[
                HumanMessage(content=message)
            ]
        }
        # 2.2 准备好配置信息，包括thread_id
        Config = {
            "configurable":{
                "thread_id":str(thread_id)
            }
        }
        # 2.3 通过智能体发送消息给大模型
        response = await self.agent.ainvoke(
            Input,
            Config
        )
        # 2.4 从返回值中解析到最后一条消息，再拿出来其中的内容
        return response["messages"][-1].content