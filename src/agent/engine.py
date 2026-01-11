import re
import json
import logging
import traceback
from typing import Optional, Tuple, Dict, Any

logger = logging.getLogger(__name__)

class ReActEngine:
    """
    ReAct 循环执行引擎
    负责: Think -> Act -> Observe 的循环调度
    """
    def __init__(self, agent, max_steps: int = 20):
        self.agent = agent
        self.max_steps = max_steps
        
        # 预编译正则，用于从 LLM 回复中提取工具调用信息
        # 匹配格式: Action: tool_name
        self.action_pattern = re.compile(r"Action:\s*(.+)")
        # 匹配格式: Action Input: {json_content}
        self.input_pattern = re.compile(r"Action Input:\s*(.+)", re.DOTALL)

    def execute(self) -> str:
        """执行 ReAct 循环"""
        logger.info(f"--- [Engine] 启动推理循环 (Max Steps: {self.max_steps}) ---")
        
        step_count = 0
        final_answer = None

        while step_count < self.max_steps:
            step_count += 1
            logger.info(f"[Step {step_count}] 正在思考...")

            # 1. 调用 LLM 生成当前的 Thought/Action
            # agent.history 包含了之前的 System Prompt 和所有交互记录
            try:
                response = self.agent.llm.generate(self.agent.history)
            except Exception as e:
                return f"LLM 调用出错: {str(e)}"
            
            # 将 LLM 的回复追加到历史记录
            self.agent.history.append({"role": "assistant", "content": response})
            logger.info(f"LLM 回复:\n{response}")

            # 2. 检查是否出现最终答案
            if "Final Answer:" in response:
                final_answer = response.split("Final Answer:")[-1].strip()
                logger.info(f"捕获最终答案，循环结束。")
                return final_answer

            # 3. 解析 Action
            # 如果没有 Final Answer，那必须有 Action
            tool_name, tool_input = self._parse_response(response)
            
            if not tool_name:
                # 如果既没有最终答案，也没有检测到工具调用，可能模型“迷路”了
                # 我们可以给它一个提示，让它继续尝试
                warning = "System Warning: 未检测到合法的 'Action:' 或 'Final Answer:'，请严格遵循格式。"
                self.agent.history.append({"role": "user", "content": warning})
                continue

            # 4. 执行工具 (Action -> Observation)
            observation = self._execute_tool(tool_name, tool_input)
            
            # 5. 将观察结果反馈给 LLM
            logger.info(f"观察结果 (Observation): {observation}")
            feedback = f"Observation: {observation}"
            self.agent.history.append({"role": "user", "content": feedback})

        return "错误: 达到最大推理步数，未能得出结论。"

    def _parse_response(self, text: str) -> Tuple[Optional[str], Optional[Dict]]:
        """从文本中解析工具名和参数"""
        action_match = self.action_pattern.search(text)
        input_match = self.input_pattern.search(text)

        if action_match and input_match:
            tool_name = action_match.group(1).strip()
            input_str = input_match.group(1).strip()
            
            # 尝试清理 JSON 字符串 (处理常见的 Markdown 格式包裹)
            input_str = input_str.replace("```json", "").replace("```", "").strip()
            
            try:
                # 尝试解析参数
                tool_args = json.loads(input_str)
                return tool_name, tool_args
            except json.JSONDecodeError:
                logger.error(f"JSON 解析失败: {input_str}")
                return None, None
        
        return None, None

    def _execute_tool(self, tool_name: str, args: Dict) -> str:
        """调用 Agent 中绑定的工具"""
        tool_func = self.agent.tools.get(tool_name)
        
        if not tool_func:
            return f"Error: 工具 '{tool_name}' 不存在。"

        try:
            logger.info(f"执行工具: {tool_name} 参数: {args}")
            # 调用工具函数
            # 注意: 这里假设工具函数接受 **kwargs 或者对应的参数名
            result = tool_func.run(**args)
            return str(result)
        except Exception as e:
            logger.error(f"Error executing tool {tool_name}", exc_info=True)
            return f"Error executing tool {tool_name}: {str(e)}"