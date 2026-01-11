import json

from src.tool.base import BaseTool

class CorpusTool(BaseTool):
    name = "tool_search_corpus"
    description = (
        "检索文献语料库，查找异文、通假例证或相关用例。"
        "参数: {'keyword': '查询关键词'}"
    )

    def run(self, keyword: str) -> str:
        # 模拟数据：搜索 "崇朝" 或 "崇" 的相关训诂材料
        mock_evidence = [
            {
                "source": "《尔雅·释诂》",
                "content": "崇，终也。",
                "note": "直接的训诂证据。"
            },
            {
                "source": "《韩诗外传》",
                "content": "崇朝，终朝也。",
                "note": "指出在'崇朝'一词中，崇即终之意，指整个早晨。"
            }
        ]

        return json.dumps(mock_evidence, ensure_ascii=False)