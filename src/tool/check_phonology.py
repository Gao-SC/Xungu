import json

from src.tool.base import BaseTool

class PhonologyTool(BaseTool):
    name = "tool_check_phonology"
    description = (
        "查询两个字的上古音韵关系（声母、韵部），判断是否音近。"
        "参数: {'char_a': '字A', 'char_b': '字B'}"
    )

    def run(self, char_a: str, char_b: str) -> str:
        # 模拟数据：崇 vs 终 (均属 冬部)
        # 上古拟音仅为示意
        if char_a == "崇" and char_b == "终":
            result = {
                "char_a": {"onset": "崇母 (dz)", "rhyme_group": "冬部 (ong)"},
                "char_b": {"onset": "章母 (t)", "rhyme_group": "冬部 (ong)"},
                "relation": "叠韵 (Rhyme overlap)",
                "conclusion": "二者韵部相同，声母发音部位相近，语音关系极密切。"
            }
        else:
            result = {"relation": "无明显语音关系"}

        return json.dumps(result, ensure_ascii=False)