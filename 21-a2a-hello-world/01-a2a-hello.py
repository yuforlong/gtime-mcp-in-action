import sys
import os

# 获取脚本所在目录的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取父目录 (mcp-in-action) 的路径
parent_dir = os.path.dirname(script_dir)
# 将父目录添加到 sys.path 的开头
sys.path.insert(0, parent_dir)

# 使用下面的正确导入路径
from A2A.samples.python.common.types import AgentSkill

def main():
  skill = AgentSkill(
    id="my-project-echo-skill",
    name="Echo Tool",
    description="Echos the input given",
    tags=["echo", "repeater"],
    examples=["I will see this echoed back to me"],
    inputModes=["text"],
    outputModes=["text"],
  )
  print(skill)

if __name__ == "__main__":
  main()