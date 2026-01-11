import json
import logging
from typing import List
from src.tool.base import BaseTool

logger = logging.getLogger(__name__)


class AnalyzeTermsTool(BaseTool):
    name = "tool_analyze_terms"
    description = (
        "分析训诂解释句中是否包含特定的术语。"
        "参数: {'explanation': '完整的训诂解释句子'}"
    )

    def run(self, explanation: str) -> str:
        # 定义常见的假借术语库
        loan_terms = ["读为", "读曰", "读如"]

        # 检查释句中是否包含目标词
        found_loan_terms = [term for term in loan_terms if term in explanation]

        result = {
            "has_loan_terms": len(found_loan_terms) > 0,
            "found_terms": found_loan_terms,
            "analysis": ""
        }

        if result["has_loan_terms"]:
            result["analysis"] = f"发现显性假借术语：{found_loan_terms}，倾向于判定为【揭明假借】。"
        else:
            result["analysis"] = "未发现显性假借术语，需结合语义和语音维度综合判断。"

        logger.info(f"[AnalyzeTermsTool] 分析结果: {result['analysis']}")
        return json.dumps(result, ensure_ascii=False)