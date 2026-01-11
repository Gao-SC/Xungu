import json
import logging
from typing import List, Dict, Optional, Any
from src.agent.prompts import EXTRACTION_PROMPT, SYSTEM_PROMPT_TEMPLATE
from src.tool import get_tools_description, create_tools

logger = logging.getLogger(__name__)

class XunguAgent:
    def __init__(self, llm_client):
        self.llm = llm_client

        # 构建调用工具列表
        self.tool_instances = create_tools(llm_client=llm_client)
        self.tools = {t.name: t for t in self.tool_instances}

        self.history = [] # 历史对话数据，记忆区
        self.engine = None

    def bind_engine(self, engine):
        """绑定执行引擎"""
        self.engine = engine

    def extract_task_info(self, user_query: str) -> Dict[str, str]:
        """
        使用 LLM 从用户输入问题中提取原始句子和解释句子
        """
        # 1. 构造 prompt
        content = EXTRACTION_PROMPT.format(user_query=user_query)
        
        # 2. 调用 LLM 
        messages = [{"role": "user", "content": content}]
        
        logger.info(f"--- [Pre-Stage] 正在提取任务信息 ---")
        try:
            response_text = self.llm.generate(messages)
            
            # 3. 清洗并解析 JSON
            # 有时候大模型会返回 ```json ... ```，需要清理掉
            clean_text = response_text.replace("```json", "").replace("```", "").strip()
            return json.loads(clean_text)
        except Exception as e:
            logger.warning(f"提取失败，启用兜底策略: {e}")
            # 兜底返回，避免程序崩溃
            return {
                "original_sentence": "未知",
                "explanation_sentence": "未知",
                "user_intent": "unknown"
            }

    def run_diagnosis(self, user_query: str):
        """
        判断主流程，根据用户输入提取后按照五大步骤进行判断
        """
        if not self.engine:
            raise ValueError("Engine not bound! Please call agent.bind_engine(engine) first.")

        # --- 准备步骤：信息提取 ---
        extracted_info = self.extract_task_info(user_query)
        
        original = extracted_info.get("original_sentence", "未提取到")
        explanation = extracted_info.get("explanation_sentence", "未提取到")
        tool_list_str = get_tools_description(list(self.tools.values()))

        logger.info(f"--- [Diagnosis Setup] 原始语境: {original} 训诂解释: {explanation}---")
        logger.info(f"构建工具列表和说明文档：{tool_list_str}")

        # --- 构建 System Prompt ---
        system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            user_query=user_query,
            original_sentence=original,
            explanation_sentence=explanation,
            tool_list=tool_list_str
        )

        # 初始化对话历史
        self.history = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"请根据原始句子“{original}”，开始对释句“{explanation}”进行训诂类型判定。"}
        ]

        # --- 启动引擎 ---
        # 将控制权交给 Engine，它会负责维护后续的 history
        result = self.engine.execute()
        return result