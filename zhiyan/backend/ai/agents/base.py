from typing import Literal,Any
from pydantic import BaseModel,Field
from langchain_core.messages import AIMessage,HumanMessage,SystemMessage
import logging

logger = logging.getLogger(__name__)

_ROLE_MAP = {
    'user':HumanMessage,
    'system':SystemMessage,
    'assistant':AIMessage
}

def to_langchain_messages(messages:list)->list:
    '''将[(role,content)]统一转为langchain消息对象列表'''
    result = []
    for m in messages:
        cls = _ROLE_MAP.get(m['role'])
        if cls:
            result.append(cls(content=m['content']))
    return result




class AgentResult(BaseModel):
    '''所有的agent统一返回格式'''
    output : str = Field(description='最终回复')
    intermediate_steps : list[dict[str,Any]] = Field(default=[],description='工具调用记录')
    requires_confirmation : bool = Field(default=False,description='是否需要用户确认')
    confirmation_data : dict[str,Any] = Field(default={},description='确认数据(高风险的时候用)')
    