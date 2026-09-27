from typing import Annotated
from fastapi import APIRouter, Header, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from app.infra.database import get_session
from app.modules.chat.schemas import ChatRequest
from app.modules.chat.service import ChatService
from fastapi.sse import ServerSentEvent, EventSourceResponse

router = APIRouter(prefix="/api/v1/chat", tags=["聊天业务"])

async def get_service(
        request:Request,
        session:AsyncSession = Depends(get_session),
):
    return ChatService(session, request.app.state.agent)

@router.post("", summary="与AI交互聊天", response_class=EventSourceResponse)
async def chat_stream(
    chat_request:ChatRequest,
    user_id:Annotated[int, Header(alias="x-user-id")],
    service:ChatService = Depends(get_service)
):
    # return await service.chat_stream(chat_request.thread_id, user_id, chat_request.message)
    # 作为下游，至少在当前的业务中不需要再对流中的数据进行处理了。
    # 所以每从流中拿到一个SSE对象，直接使用yield将数据放到流中。
    # 其实下游就是EventSourceResponse，那剩下的就是EventSourceResponse的事情了。
    # EventSourceResponse会逐个遍历生成器，每接收到一个数据，会立刻将SSE按照特有的响应头发送到前端~那就结束了，最后一个环节了
    """
    至于为什么使用async for，生成器之间的对接就是靠 async for ... yield 这种写法，记住就可以了。
    以后只要别人给你yield很多数据，你就用async for来同步接收并处理~

    你看，使用yield再配合async，组装一个流还是挺方便的.
    更底层中的流也是使用的yield来回传数据的~直到有人处理这个流中的数据，或者流中的数据被丢掉，一个完整的流式调用链路就算是结束了

    不一定能听懂，已经很底层了，能听懂就听懂，听不懂就记住，流式输出就这么玩儿~
    """
    async for sse in service.chat_stream(chat_request.thread_id, user_id, chat_request.message):
        yield sse