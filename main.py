from src.agent.core import XunguAgent
from src.agent.client import Client
from src.agent.engine import ReActEngine
from src.tool import create_tools

import logging

logging.basicConfig(
    level=logging.DEBUG, # 设置为 INFO 或 WARNING 即可隐藏 DEBUG 信息
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
# 屏蔽第三方库的繁琐 DEBUG 日志
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

def main():
    logger.info("启动训诂智能体系统...")

    # 1. 初始化LLM端
    llm_client = Client()

    # 2. 使用工厂函数一键组装所有工具，并注入 client 依赖
    # tool_list = create_tools(llm_client)
    # logger.debug(tool_list)
    # logger.info(f"已加载 {len(tool_list)} 个工具。")

    # 3. 初始化agent
    agent = XunguAgent(llm_client=llm_client)
    engine = ReActEngine(agent)
    agent.bind_engine(engine)

    # 4. 创建查找实例
    user_input = input("请输入问题\n")

    # 6. 智能体将自动处理：提取信息 -> 构建 Prompt -> 执行 ReAct 循环
    try:
        result = agent.run_diagnosis(user_query=user_input)
        print(result)
    except Exception as e:
        logger.error(f"\n 运行过程中发生错误: {e}")


if __name__ == "__main__":
    main()