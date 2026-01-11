import json
from src.tool.base import BaseTool


class VerifyContextTool(BaseTool):
    name = "tool_verify_context"
    description = (
        "将两个字的义项分别代入原句，验证语境通顺度。"
        "参数: {'original_sentence': '原句', 'char_a': '被训字A', 'char_a_meaning': '被训字A义', 'char_b': '训字B', 'char_b_meaning': '训字B义'}"
    )

    def __init__(self, llm_client):
        """
        工具内部需要调用大模型来进行语义判断。
        """
        self.llm_client = llm_client

    def run(self, original_sentence: str, char_a: str, char_a_meaning: str, char_b: str, char_b_meaning: str) -> str:
        # 构造一个专门用于判定的内部 Prompt
        # 这是一个“大模型套小模型”的经典用法
        internal_prompt = f"""
        你是一个古汉语学家，请进行一项还原语境适配度的操作，判断哪个义项代入原句更通顺。

        原始句子：{original_sentence}

        待验证方案：
        1. 字 A ({char_a}) 本义代入：意思为“{char_a_meaning}”
        2. 字 B ({char_b}) 本义代入：意思为“{char_b_meaning}”

        判断标准：
        - 结合古代文献语境。
        - 只要告诉我哪个方案在逻辑和语义上更通顺。
        - 如果方案 A 不通，而方案 B 通顺，请明确指出。

        请简短地输出判断结果，控制在100字以内，不需要包含其它文本：
        """

        # 调用 LLM (注意适配 client 的 messages 格式)
        messages = [{"role": "user", "content": internal_prompt}]
        try:
            # 复用主程序的 client 进行生成
            analysis_result = self.llm_client.generate(messages)
            return f"语境验证结果：{analysis_result}"
        except Exception as e:
            return f"Error during context verification: {str(e)}"