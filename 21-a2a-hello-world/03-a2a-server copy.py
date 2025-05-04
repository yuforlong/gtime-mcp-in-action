# -*- coding: utf-8 -*-
"""
A2A Echo Agent 主程序入口。
定义 Agent Card，设置 Task Manager，并启动 A2A 服务器。
"""

# --- Start: sys.path modification to find A2A module ---
import sys
import os

# 获取脚本所在目录的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取父目录 (mcp-in-action or the directory containing A2A)
# 注意: 如果你的脚本在 src/my_project/ 下，可能需要再多一个 os.path.dirname
# 假设脚本就在 21-a2a-hello-world 下，A2A 在上一级
parent_dir = os.path.dirname(script_dir)
# 将包含 A2A 的目录添加到 sys.path 的开头
sys.path.insert(0, parent_dir)
# --- End: sys.path modification ---

# --- Start: Imports ---
import logging

import click # 用于处理命令行参数

# 从修改后的路径导入 A2A 相关类
from A2A.samples.python.common.server import A2AServer
from A2A.samples.python.common.types import AgentSkill, AgentCapabilities, AgentCard

# 从本项目导入我们自己定义的 Task Manager
# 使用相对导入 '.' 表示从当前目录 (src/my_project)
from task_manager import MyAgentTaskManager
# --- End: Imports ---

# --- Start: Logging Setup ---
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)
# --- End: Logging Setup ---


# --- Start: Main application logic ---
@click.command()
@click.option("--host", default="localhost", help="服务器绑定的主机地址。")
@click.option("--port", default=10002, type=int, help="服务器绑定的端口号。")
def main(host, port):
  """
  主函数：定义代理技能和名片，创建任务管理器和服务器，并启动服务器。
  """
  # 1. 定义代理技能 (Skill)
  skill = AgentSkill(
    id="my-project-echo-skill", # 技能的唯一ID
    name="Echo Tool",          # 技能名称
    description="Echos the input given", # 技能描述
    tags=["echo", "repeater"], # 标签，用于分类或搜索
    examples=["I will see this echoed back to me"], # 使用示例
    inputModes=["text"],      # 支持的输入模式
    outputModes=["text"],     # 支持的输出模式
  )
  logger.info("代理技能定义完成。")

  # 2. 定义代理能力 (Capabilities)，这里使用默认值
  capabilities = AgentCapabilities()
  logger.info("代理能力定义完成。")

  # 3. 定义代理名片 (Agent Card)，包含元数据和技能列表
  agent_card = AgentCard(
    name="Echo Agent",         # 代理名称
    description="This agent echos the input given", # 代理描述
    url=f"http://{host}:{port}/", # 代理的访问地址 (动态生成)
    version="0.1.0",          # 代理版本
    defaultInputModes=["text"], # 默认输入模式
    defaultOutputModes=["text"],# 默认输出模式
    capabilities=capabilities, # 代理能力
    skills=[skill]            # 代理提供的技能列表 (包含上面定义的 skill)
  )
  logger.info(f"代理名片生成完成:\n{agent_card}")

  # 4. 创建我们自定义的任务管理器实例
  task_manager = MyAgentTaskManager()
  logger.info("任务管理器实例化完成。")

  # 5. 创建 A2A 服务器实例
  server = A2AServer(
    agent_card=agent_card,     # 传入代理名片
    task_manager=task_manager, # 传入任务管理器
    host=host,                 # 传入监听的主机地址
    port=port,                 # 传入监听的端口号
  )
  logger.info(f"A2A 服务器准备就绪，将在 http://{host}:{port}/ 启动。")

  try:
    # 6. 启动服务器 (此调用会阻塞，直到服务器停止)
    server.start()
    logger.info("服务器已启动。")
  except Exception as e:
    logger.error(f"服务器启动失败: {str(e)}")
    raise

# --- End: Main application logic ---


# --- Start: Script execution entry point ---
if __name__ == "__main__":
  # 当脚本被直接运行时，调用 main 函数
  main()
# --- End: Script execution entry point ---