from .base import AgentResult,to_langchain_messages
from ai.llm import ZhiYanLLM
import logging

logger = logging.getLogger(__name__)

class GeneralAgent:
    '''通用对话Agent(没有工具,纯LLM回答)'''
    
    def __init__(self):
        self.llm = ZhiYanLLM().llm
    
    def stream(self,messages):
        langchain_messages = to_langchain_messages(messages)
        full = ''
        try:
            for chunk in self.llm.stream(langchain_messages):
                if chunk.content:
                    full += chunk.content
                    yield {"type":"token","content":chunk.content}
        except Exception as e:
            logger.error(f'GeneralAgent stream异常:{e}')
            if full:
                yield {"type":"token","content":"\n\n[系统繁忙，请稍后重试！]"}
        finally:
            yield {"type":"done","full_response":full}
    def run(self,messages):
        full = ''
        for event in self.stream(messages):
            if event['type'] == 'token':
                full += event['content']
        return AgentResult(output=full)
    
        