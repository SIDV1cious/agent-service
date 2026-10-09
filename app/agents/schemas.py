from typing import Literal

from langgraph.graph import MessagesState
from pydantic import BaseModel, Field

# 1.定义节点的名称：实际上是在定义一个类型别名（Type Alias），这意味着以后可以用 Intent 作为类型注解。
# Literal 是 Python 类型系统提供的一种字面量类型（Literal Type），用于限制一个变量只能取指定的几个值。
Intent = Literal[
    "chitchat",             # 聊天节点名称
    "recommendation_plan",  # 保险推荐节点名称
    "claim",                # 理赔节点名称
    "human_handoff",        # 人工客服节点名称
    "fallback",             # 意图识别失败之后的节点名称
]

# 2.定义主图的流转状态
class InsuranceAgentState(MessagesState):
    # 1.上一轮会话意图识别的结果
    previous_workflow:str
    # 2.本轮对话意图识别的结果
    active_workflow:str

# 3.定义BaseModel模型，限制意图识别的结果
class IntentResult(BaseModel):
    # 1.意图识别的结果
    intent:Intent = Field(description="本轮对话意图识别的结果")
    # 2.判断依据
    reason:str = Field(description="意图识别的依据、原因")