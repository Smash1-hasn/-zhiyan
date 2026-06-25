import os
os.environ['DEEPSEEK_API_KEY'] = 'sk-ada5ebc08baf421fb9812adbcaf47946'

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage

@tool
def query_order(order_id: str) -> str:
    """查询订单状态"""
    return f"订单 {order_id} 已发货"

llm = ChatOpenAI(
    model='deepseek-chat',
    openai_api_key=os.environ['DEEPSEEK_API_KEY'],
    openai_api_base='https://api.deepseek.com'
)

agent = create_agent(llm, [query_order], system_prompt="你是智能客服")

result = agent.invoke({"messages": [HumanMessage("查一下 OR2024001")]})
print("Result:", result)
