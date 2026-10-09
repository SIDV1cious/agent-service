from langchain.chat_models import init_chat_model
from langchain_core.messages import AIMessage, SystemMessage, HumanMessage
from langgraph.graph import StateGraph
from app.agents.schemas import InsuranceAgentState
from app.core.config import settings


# 定义闲聊子节点的状态,active_workflow和messages直接继承父类的属性
class ChitchatState(InsuranceAgentState):
    chitchat_count:int # 闲聊的次数

MAX_CHITCHAT_COUNT = 3

SYSTEM_MESSAGE = """
你是保险智能客服，负责处理与保险业务无关的普通聊天。

要求：
1. 回复友好、自然，最多两句话。
2. 不假装有个人经历、情感、实时信息或外部能力。
3. 不回答医疗、法律、投资等高风险专业建议。
4. 每次回复都自然引导用户回到保险产品、投保或理赔业务。
5. 超出能力范围时，如实说明无法提供。
""".strip()

class ChitchatAgent:

    def __init__(self):
        # 1.初始化模型
        self.model = init_chat_model(
            model="deepseek-flash",
            api_key=settings.llm.api_key,
            extra_body={
                "thinking":{
                    "type":"disabled"
                }
            }
        )

    async def handle_chat(self, state:ChitchatState):
        # 1.获取已有的聊天次数
        count = state.get("chitchat_count", 0)
        # 2.判断上一个流程是否是聊天，如果不是聊天，聊天次数要重置
        if state["previous_workflow"] != 'chitchat':
            count = 0
        # 3.如果是聊天已经超过了最大次数，返回一个固定回答
        if count >= MAX_CHITCHAT_COUNT:
            return {
                "messages":[AIMessage(content="我主要协助处理保险产品、投保和理赔咨询，请告诉我想办理或了解的事项。")]
            }
        # 4.与大模型进行交互
        response:AIMessage = await self.model.ainvoke([
            SystemMessage(content=SYSTEM_MESSAGE),
            *state["messages"]
        ])
        return {
            "messages":[response],
            "count":count + 1
        }


    def builder(self):
        # 1.创建构建器
        builder = StateGraph(ChitchatState)
        # 2.添加节点
        builder.add_node("handler_chitchat", self.handle_chat)
        # 3.添加边构建图
        builder.set_entry_point("handler_chitchat")
        builder.set_finish_point("handler_chitchat")
        # 4.编译智能体
        agent = builder.compile(checkpointer=True)

        return agent