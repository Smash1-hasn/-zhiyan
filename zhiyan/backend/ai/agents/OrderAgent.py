from langchain.agents import create_agent
from .base import AgentResult,to_langchain_messages
from ai.llm import ZhiYanLLM
from ai.tools import query_order
import logging

logger = logging.getLogger(__name__)

class OrderAgent:
    def __init__(self):
        self.llm = ZhiYanLLM().llm
        self.tools = [query_order]
        self.agent = create_agent(
            self.llm,
            self.tools,
            system_prompt=(
                "你是一个订单查询助手。\n"
                "职责：帮用户查询订单状态和物流信息。\n"
                "如果用户问非订单问题，礼貌引导回订单话题。\n"
                "始终用中文回答。"
            )
        )
    def stream(self,messages):
        '''流式执行，yield标准化事件'''
        langchain_messages = to_langchain_messages(messages)
        full= ''
        try:
            for event in self.agent.stream({'messages':langchain_messages}):
                if not isinstance(event,dict):
                    continue
                for node,output in event.items():
                    if not isinstance(output,dict):
                        continue
                    for msg in output.get('messages',[]):
                        if not hasattr(msg,'type'):
                            continue
                        if msg.type == 'ai' and msg.content:
                            full += msg.content
                            yield {"type":"token","content":msg.content}
                        if hasattr(msg,'tool_calls') and msg.tool_calls:
                            for tc in msg.tool_calls:
                                yield {"type":"tool_call","tool":tc.get("name"),"args":tc.get('args')}
                        if msg.type == 'tool' and hasattr(msg,"content"):
                            yield {"type":"tool_result","content":msg.content}
        except Exception as e:
            logger.error(f'OrderAgent stream异常:{e}')
            if full:
                yield {"type":"token","content":"\n\n[系统繁忙，请稍后重试！]"}
        finally:
            yield {"type":"done","full_response":full}
   
    def run(self,messages):
        full = ''
        for event in self.stream(messages):
            if event['type'] == 'token':
                full += event["content"]
        return AgentResult(output=full)
    
        