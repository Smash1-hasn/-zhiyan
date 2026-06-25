导入 os
os.environ['DEEPSEEK_API_KEY'] 

从 langchain.agents 导入 create_agent
从 langchain_core.tools 导入 tool
从 langchain_openai 导入 ChatOpenAI
从 langchain_core.messages 导入 HumanMessage

@tool
def 查询订单(订单ID：str) -> str：
    """查询订单状态"""
    返回 f"订单 {订单ID} 已发货"

llm = ChatOpenAI(
    model='deepseek-chat',
    openai_api_key=os.environ['DEEPSEEK_API_KEY'],
    openai_api_base='https://api.deepseek.com'
)

agent = create_agent(llm, [查询订单], system_prompt="你是智能客服")

result = agent.调用({"消息": [人类消息("查询 OR2024001")]})
打印("结果：", 结果)
