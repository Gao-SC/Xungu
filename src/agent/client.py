import os
import logging
from openai import OpenAI
from typing import List, Dict

logger = logging.getLogger(__name__)

class Client:
    def __init__(self):
        self.client = OpenAI(
            api_key= "sk-ba540df69ecc44d596e38717883956b4",#os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://api.deepseek.com/v1"
        )
        self.model = "deepseek-reasoner"

    def generate(self, messages: List[Dict[str, str]]) -> str:
        """
        支持多轮对话的生成函数
        :param messages: 对话历史列表,格式如 [{"role": "user", "content": "..."}, ...]
        :return: 模型生成的回复文本
        """
        try:
            # logger.debug("Connecting to LLM...") 
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                # 设置停止词: 当模型试图生成 "Observation:" 时，API 会强制截断并返回
                stop = ["Observation:", "Observation：", "observation:", "observation："]
            )
            return completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error calling LLM: {e}")
            # 返回一个空字符串或错误提示，防止程序崩溃
            return ""