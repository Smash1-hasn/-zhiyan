from pydantic import BaseModel, Field
from ai.llm import ZhiYanLLM
import logging

logger = logging.getLogger(__name__)


class IntentResult(BaseModel):
    intent: str = Field(description="order_query / after_sales / general")
    reasoning: str = Field(description="判断理由")


class IntentClassifier:
    def __init__(self):
        self.structured_llm = ZhiYanLLM().llm.with_structured_output(IntentResult)

    def classify(self, message: str) -> IntentResult:
        try:
            prompt = (
                "你是一个客服系统的意图识别器。\n"
                "分析用户消息，属于哪一类：\n"
                "- order_query: 查询订单状态、物流信息\n"
                "- after_sales: 退换货、退款、售后问题\n"
                "- general: 其他问题、闲聊、问候\n\n"
                f"用户消息：{message}"
            )
            return self.structured_llm.invoke(prompt)
        except Exception as e:
            logger.error(f"意图分类异常: {e}")
            return IntentResult(intent="general", reasoning="分类异常，默认走通用")
