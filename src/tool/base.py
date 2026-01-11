from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseTool(ABC):
    name: str = ""
    description: str = ""

    @abstractmethod
    def run(self, **kwargs) -> str:
        """
        子类必须实现这个方法，执行具体的业务逻辑。
        返回结果必须是字符串（因为要喂回给大模型）。
        """
        pass

    def get_prompt_format(self) -> str:
        """
        自动生成给 System Prompt 看的工具描述。
        格式示例:
        1. tool_name: 描述信息。参数: {...}
        """
        return f"{self.name}: {self.description}"