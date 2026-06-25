from langchain.agents import create_agent
from ai.llm import ZhiYanLLM
from .base import AgentResult,to_langchain_messages
from ai.tools import return_policy,submit_refund
import logging

logger = logging.getLogger(__name__)

class AfterSalesAgent:
    '''售后Agent'''
    def __init__(self):
        self.llm = ZhiYanLLM().llm
        self.tools = [return_policy,submit_refund]
        self.agent = create_agent(
            self.llm,
            self.tools,
            system_prompt=(
                "你是一个售后处理助手。\n"
                "职责：解答退换货规则、处理退款申请。\n\n"
                "工作流程：\n"
                "- 如果用户询问退换货规则 → 调 return_policy 查询规则并告知用户\n"
                "- 如果用户主动申请退款（提供了订单号、金额、原因）→ 直接调 submit_refund 提交\n"
                "  submit_refund 是高风险操作，提交后系统会自动要求用户二次确认，你不需要自己确认\n"
                "- 不要替用户做决定，也不要自己编造退款结果，让工具返回实际结果\n\n"
                "始终用中文回答。"
            )

        )
    
    def stream(self,messages):
        '''流式执行，yield标准化事件'''
        langchain_messages = to_langchain_messages(messages)
        full= ''
        has_refund = False
        refund_data = {}
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
                                if tc.get("name") == 'submit_refund':
                                    has_refund = True
                                    refund_data = tc.get('args',{})
                        if msg.type == 'tool' and hasattr(msg,"content"):   
                            yield {"type":"tool_result","content":msg.content}
        except Exception as e:
            logger.error(f'AfterSalesAgent stream异常:{e}')
            if full:
                yield {"type":"token","content":"\n\n[系统繁忙，请稍后重试！]"}
        finally:
            yield {"type":"done","full_response":full,"has_refund":has_refund,"refund_data":refund_data}
   
    def run(self,messages):
        full = ''
        for event in self.stream(messages):
            if event['type'] == 'token':
                full += event["content"]
        return AgentResult(output=full)
    
        