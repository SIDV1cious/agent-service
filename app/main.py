from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import configure_logging, get_logger
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.core.exceptions import ApplicationError

# 初始化日志系统
configure_logging(settings.logging.level)
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app:FastAPI):
    """
    生命周期管理函数
    :param app: FastAPI实例
    """
    # 1.FastAPI刚刚启动的时候执行的代码逻辑
    # 1.1 导入check_database和close_database,加载database模块
    from app.infra.database import check_database, close_database
    # 1.2 执行数据库连接的初始化操作
    await check_database()
    logger.info("数据库连接初始化完成~")
    # 1.3 导入初始化方法和关闭方法（checkpointer）
    from app.infra.checkpointer import init_checkpointer, close_checkpointer
    # 1.4 执行初始化操作
    checkpointer = await init_checkpointer()
    # 1.5 创建全局保险顾问智能体
    from app.agents.insurance_advisor import init_insurance_advisor
    agent = await init_insurance_advisor(checkpointer)
    app.state.agent = agent
    # 1.6 初始化模块级别的pipeline retriever close_rag - 只需要导入就会自动的初始化
    from app.rag import close_rag

    yield
    # 2.项目关闭的时候执行的一些代码逻辑
    # 2.1 执行数据库连接的关闭操作
    await close_database()
    logger.info("数据库连接关闭完成~")
    # 2.2 执行关闭数据库连接池的方法
    await close_checkpointer()
    # 2.3 关闭RAG资源
    close_rag()

app = FastAPI(
    title=settings.app.name,
    debug=settings.app.debug,
    lifespan=lifespan
)

@app.exception_handler(ApplicationError)
async def handle_application_error(
    request: Request,
    exc: ApplicationError, # 捕获到的异常（这里用自定义异常基类捕获，所有业务异常都会匹配到）
) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code, # 异常中自带status
        content={
            "code": exc.code,        # 异常中自带code
            "message": exc.message,  # 异常中自带message
        },
    )

from app.modules.product.router import router as product_router
app.include_router(product_router)

from app.modules.chat_thread.router import router as chat_thread_router
app.include_router(chat_thread_router)

from app.modules.chat.router import router as chat_router
app.include_router(chat_router)

@app.get("/health", summary="健康检测接口")
async def health_check() -> dict[str, str]:
    logger.info("执行健康检查")
    return {"status": "ok"}


if __name__ == "__main__":
    import sys
    uvicorn.run(
        app,
        host=settings.app.host,
        port=settings.app.port,
        reload=False,
        loop= "asyncio:SelectorEventLoop" if sys.platform == "win32" else "auto"
    )

