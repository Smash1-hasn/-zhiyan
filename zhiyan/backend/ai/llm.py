from langchain_deepseek import ChatDeepSeek
import os
import logging

logger = logging.getLogger(__name__)


class ZhiYanLLM:
    def __init__(self,model='deepseek-chat',temperature=0.7):
        self.llm = ChatDeepSeek(
            model=model,
            temperature= temperature,
            api_key = os.getenv('DEEPSEEK_API_KEY'),

        )
    def invoke(self,messages):
        '''调用LLM,返回回复内容'''
        try:
            response = self.llm.invoke(messages)
            return response.content
        except Exception as e:
            logger.error(f'LLM invoke异常:{e}')
            raise
    def stream(self,messages):
        '''流式输出'''
        try:
            response = self.llm.stream(messages)
            for chunk in response:
                if chunk.content:
                    yield chunk.content
        except Exception as e:
            logger.error(f'LLM stream 异常:{e}')
            raise

        
        