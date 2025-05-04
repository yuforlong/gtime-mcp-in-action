'''
运行方式：
python 06-tools-工具列表/client/simple-client.py 06-tools-工具列表/server/simple-tools-v1.py
此命令将启动客户端并连接到指定的工具服务器
'''
import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.types import Notification
from mcp.client.stdio import stdio_client

async def main():
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("Usage: python simple_client.py <path_to_server_script>")
        sys.exit(1)

    server_script = sys.argv[1]
    params = StdioServerParameters(
        command="/mnt/external_disk/venv/20250426_MCP_Server/bin/python3",
        args=[server_script],
        env=None
    )

    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            # 初始化握手
            await session.initialize()
            
            # 发送初始化完成通知
            notification = Notification(
                method="notifications/initialized",
                params={}
            )
            await session.send_notification(notification)

            # 列出可用工具
            response = await session.list_tools()
            print("可用工具列表：")
            for tool in response.tools:
                print(f"- 名称: {tool.name}")
                print(f"  描述: {tool.description}")
                print(f"  输入模式: {tool.inputSchema}")
                print()

            # 测试计算器工具
            print("\n测试计算器工具:")
            calculator_result = await session.call_tool(
                name="calculator",
                arguments={
                    "operation": "add",
                    "a": 5,
                    "b": 3
                }
            )
            print(f"计算结果: {calculator_result.content[0].text}")

            # 测试文本分析工具
            print("\n测试文本分析工具:")
            text_result = await session.call_tool(
                name="text_analyzer",
                arguments={
                    "text": "这是一个测试文本，用于演示工具功能。"
                }
            )
            print(f"分析结果: {text_result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(main()) 