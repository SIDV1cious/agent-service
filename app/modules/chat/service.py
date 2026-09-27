from uuid import UUID
from langchain_core.messages import HumanMessage
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.chat_thread.exceptions import ChatThreadNotFoundError
from app.modules.chat_thread.repository import ChatThreadRepository
from fastapi.sse import ServerSentEvent

class ChatService:
    def __init__(self, session:AsyncSession, agent:CompiledStateGraph):
        self.repository = ChatThreadRepository(session)
        self.agent = agent

    async def chat_stream(self, thread_id:UUID, user_id:int, message:str):
        # 1.验证当前会话是不是属于当前登录的用户
        chat_thread =  await self.repository.find_owned(thread_id, user_id)
        if chat_thread is None:
            raise ChatThreadNotFoundError

        # 2.目标：通过智能体发送消息给大模型
        # 2.1 准备好消息列表
        _input = {
            "messages":[
                HumanMessage(content=message)
            ]
        }
        # 2.2 准备好配置信息，包括thread_id
        _config = {
            "configurable":{
                "thread_id":str(thread_id)
            }
        }
        # # 2.3 通过智能体发送消息给大模型
        # response = await self.agent.ainvoke(
        #     Input,
        #     Config
        # )
        # # 2.4 从返回值中解析到最后一条消息，再拿出来其中的内容
        # return response["messages"][-1].content

        # 2.4 流式解析：遍历每条消息，再把每条消息的文本片段逐个通过 SSE 推给前端

        """
                Asynchronous per-message streaming object for a single LLM response.
                The stream itself is awaitable (`msg = await stream`) and async-iterable (`async for event in stream`).

                单个LLM响应的异步消息流对象。
                流本身是可唤醒的（`msg = await stream`）和可同步迭代的（`async for event in stream`）。
                """
        # response.messages代表多个消息流，也就是一条条消息，包括：思考流、工具调用流和文本流消息，可以认为是一条条水管~
        # 每一次循环同步拿到一个管道，也就是一个消息流
        async for message in response.messages:
            """
            Text content — async iterable of `str` deltas, awaitable for full text.
            文本内容 - `str`增量的异步可迭代对象，对于全文能够慢慢等着输出。
            """
            # 内层：message.text代表一条消息里的文本流，你可以认为进入到一个水管中了，那水管中就会时不时的从上游流水下来，也就是一个个的文本片段。
            async for text in message.text:
                # 在这儿拿到一个消息片段之后，使用yield，将数据组装成SSE对象放到了一个管道（流）中，往下游流
                yield ServerSentEvent(event="message", data=text)
        yield ServerSentEvent(event="done", data="END")