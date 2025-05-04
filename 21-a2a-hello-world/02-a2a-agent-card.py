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

import click # For command-line arguments
# Removed dotenv import for now as it's not used in the snippet
# from dotenv import load_dotenv

# Import types from the cloned A2A library using the modified path
from A2A.samples.python.common.types import AgentSkill, AgentCapabilities, AgentCard
# --- End: Imports ---

# --- Start: Logging Setup ---
# Basic logging configuration
logging.basicConfig(level=logging.INFO, format='%(levelname)s:%(name)s:%(message)s')
# Get a logger instance (optional, can also use root logger)
logger = logging.getLogger(__name__) # Often use __name__ for the logger
# --- End: Logging Setup ---


# --- Start: Main application logic decorated with click ---
@click.command()
@click.option("--host", default="localhost", help="Host to bind the agent server to.")
@click.option("--port", default=10002, type=int, help="Port to bind the agent server to.")
def main(host, port):
  """
  Defines an Echo Agent Skill and Agent Card, then logs the Agent Card.
  This version does not yet start a server.
  """
  # 1. Define the Skill
  skill = AgentSkill(
    id="my-project-echo-skill",
    name="Echo Tool",
    description="Echos the input given",
    tags=["echo", "repeater"],
    examples=["I will see this echoed back to me"],
    inputModes=["text"],
    outputModes=["text"],
  )
  # Log the skill details (optional)
  # logging.info(f"Defined Skill: {skill}") # Using f-string for potentially better formatting

  # 2. Define Capabilities (currently empty/default)
  capabilities = AgentCapabilities()

  # 3. Define the Agent Card
  agent_card = AgentCard(
    name="Echo Agent",
    description="This agent echos the input given",
    url=f"http://{host}:{port}/", # Dynamically create the URL
    version="0.1.0",
    defaultInputModes=["text"],
    defaultOutputModes=["text"],
    capabilities=capabilities,
    skills=[skill] # List containing the skill(s) this agent offers
  )

  # 4. Log the Agent Card information
  # Using logger instance is often preferred over root logger (logging.info)
  logger.info(f"Generated Agent Card:\n{agent_card}") # Log the agent card

  # Note: This function currently just defines and logs.
  # A real agent would proceed to start a server here using host and port.

# --- End: Main application logic ---


# --- Start: Script execution entry point ---
if __name__ == "__main__":
  main()
# --- End: Script execution entry point ---