import asyncio
from fastmcp import Client
from fastmcp.client.transports import FastMCPTransport
from hello_tool import mcp  # 替换为您的服务器文件名

async def main():
    async with Client(FastMCPTransport(mcp)) as client:
        result = await client.call_tool("add", {"a": 5, "b": 7})
        print("Result:", result)

if __name__ == "__main__":
    asyncio.run(main())