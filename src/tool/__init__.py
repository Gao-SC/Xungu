# src/tools/__init__.py

from typing import List
from .base import BaseTool
from .search_dictionary import DictionaryTool
from .check_phonology import PhonologyTool
from .search_corpus import CorpusTool
from .analyze_terms import AnalyzeTermsTool
from .verify_context import VerifyContextTool


def create_tools(llm_client) -> List[BaseTool]:
    """
    工厂函数：初始化所有工具
    """
    return [
        DictionaryTool(),
        PhonologyTool(),
        CorpusTool(),
        AnalyzeTermsTool(),
        VerifyContextTool(llm_client)
    ]


def get_tools_description(tools: List[BaseTool]) -> str:
    """
    格式化函数：负责将工具列表转换成 System Prompt 需要的文本格式。

    Args:
        tools: 已经实例化好的工具列表

    Returns:
        str: 拼接好的工具说明书字符串
    """
    descriptions = []
    for i, tool in enumerate(tools):
        # 这里调用每个工具自己的 get_prompt_format 方法
        desc = f"{i + 1}. {tool.get_prompt_format()}"
        descriptions.append(desc)

    return "\n".join(descriptions)