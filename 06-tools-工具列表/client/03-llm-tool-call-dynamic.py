'''
运行方式：
uv run 03-llm-tool-call-dynamic.py ../server/simple-tools-v2-Protocal.py
或者
source /home/huangjia/Documents/17_MCP/mcp-in-action/06-tools-工具 列表/client/.venv/bin/activate
python 03-llm-tool-call-dynamic.py ../server/simple-tools-v2-Protocal.py
此命令将启动客户端并连接到指定的工具服务器，然后根据用户输入动态调用工具
'''
import asyncio
import sys
import json
from mcp import ClientSession, StdioServerParameters
from mcp.types import Notification
from mcp.client.stdio import stdio_client
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY"),
    base_url="https://api.deepseek.com"
)

def call_llm_with_tools(messages, tools):
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools,
        tool_choice="auto"
    )
    return response.choices[0].message

async def main():
    if len(sys.argv) < 2:
        print("Usage: python simple_client_v3.py <path_to_server_script>")
        sys.exit(1)

    server_script = sys.argv[1]
    params = StdioServerParameters(
        command="/home/huangjia/Documents/17_MCP/mcp-in-action/06-tools-工具列表/server/.venv/bin/python3",
        args=[server_script],
        env=None
    )

    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            await session.initialize()
            notification = Notification(
                method="notifications/initialized",
                params={}
            )
            await session.send_notification(notification)

            # 获取工具列表
            response = await session.list_tools()
            tools = response.tools

            print("欢迎使用工具调用系统！\n可用工具列表已加载。\n请输入您的需求（输入'退出'结束）：")

            # 构造 tools 列表
            tools_list = [{
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
            } for tool in tools]

            # 交互主循环
            messages = [
                {"role": "system", "content": "你是一个智能助手，请根据用户输入选择合适的工具并构造参数，或直接回复用户。"}
            ]
            while True:
                user_input = input("> ")
                if user_input.lower() == "退出":
                    break
                messages.append({"role": "user", "content": user_input})
                message = call_llm_with_tools(messages, tools_list)
                messages.append(message)
                if not message.tool_calls:
                    print(message.content)
                    continue
                # 工具调用
                for tool_call in message.tool_calls:
                    args = json.loads(tool_call.function.arguments)
                    result = await session.call_tool(tool_call.function.name, args)
                    messages.append({
                        "role": "tool",
                        "content": str(result),
                        "tool_call_id": tool_call.id
                    })
                # 再次让 LLM 总结最终回复（这时 messages 里有 “答案” 的内容了）
                message = call_llm_with_tools(messages, tools_list)
                print(message.content)
                messages.append(message)

if __name__ == "__main__":
    asyncio.run(main()) 