import json
from typing import List
from src.tool.base import BaseTool

class DictionaryTool(BaseTool):
    name = "tool_search_dictionary"
    description = (
        "查询字词的本义、引申义。支持批量查询。"
        "参数: {'words': ['查询词1', '查询词2']}"
    )

    def run(self, words: List[str]) -> str:
        # 模拟数据：针对 "崇" 和 "终"
        mock_data = {
            "崇": {
                "definitions": [
                    "高大 (lofty/high)",
                    "尊崇 (worship/honor)",
                    "充满 (full)"
                ],
                "explanation": "本义为山大而高。"
            },
            "终": {
                "definitions": [
                    "了结，结束 (end/finish)",
                    "死 (death)",
                    "极点 (limit)"
                ],
                "explanation": "本义为丝线绕完了。"
            }
        }

        results = {}
        for word in words:
            results[word] = mock_data.get(word, "未收录该字")

        return json.dumps(results, ensure_ascii=False)