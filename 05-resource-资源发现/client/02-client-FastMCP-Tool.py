# rag_client.py

import sys
import os
import json
import asyncio
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from openai import OpenAI
from mcp.types import Notification

load_dotenv()

class RagClient:
    def __init__(self):
        self.session = None
        self.transport = None
        self.tools = []
        self.openai = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
        )

    async def connect(self, server_script: str):
        # 1) 启动 MCP 服务器进程
        params = StdioServerParameters(
            command=sys.executable,       # 使用当前 Python 解释器
            args=[server_script],
            env=None
        )
        self.transport = stdio_client(params)
        self.stdio, self.write = await self.transport.__aenter__()

        # 2) 初始化 MCP 会话
        self.session = await ClientSession(self.stdio, self.write).__aenter__()
        await self.session.initialize()
        notification = Notification(
            method="notifications/initialized",
            params={}
        )
        await self.session.send_notification(notification)

        # 3) 获取可用工具
        resp = await self.session.list_tools()
        self.tools = [
            {
                "type": "function",
                "function": {
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.inputSchema
                }
            }
            for t in resp.tools
        ]
        print("可用工具：", [t["function"]["name"] for t in self.tools])

        # 4) 发现并读取资源
        res_list = await self.session.list_resources()
        uris = [r.uri for r in getattr(res_list, "resources", res_list)]
        print("发现资源：", uris)

        # 5) 读取并索引资源内容
        all_texts = []
        for uri in uris:
            rr = await self.session.read_resource(uri)
            for content in rr.contents:
                if hasattr(content, "text") and content.text:
                    all_texts.append(content.text)
        if all_texts:
            idx_resp = await self.session.call_tool("index_docs", {"docs": all_texts})
            print("资源文档索引：", idx_resp)

    async def query(self, q: str) -> str:
        # 构建对话
        messages = [
            {"role": "system", "content": "你是一个专业的医学助手，请根据文档回答问题。"},
            {"role": "user",   "content": q}
        ]
        while True:
            resp = self.openai.chat.completions.create(
                model="deepseek-chat",
                messages=messages,
                tools=self.tools,
                tool_choice="auto"
            )
            msg = resp.choices[0].message
            messages.append(msg)

            # 如果没有工具调用，则直接返回结果
            if not msg.tool_calls:
                return msg.content

            # 处理工具调用
            for call in msg.tool_calls:
                args = json.loads(call.function.arguments)
                result = await self.session.call_tool(call.function.name, args)
                messages.append({
                    "role": "tool",
                    "content": str(result),
                    "tool_call_id": call.id
                })

    async def close(self):
        if self.session:
            await self.session.__aexit__(None, None, None)
        if self.transport:
            await self.transport.__aexit__(None, None, None)

async def main():
    if len(sys.argv) < 2:
        print("用法: python rag_client.py <path_to_server_script>")
        sys.exit(1)

    client = RagClient()
    await client.connect(sys.argv[1])
    print('>>> 系统连接成功，您可以开始提问（输入"退出"结束）')

    try:
        while True:
            q = input("\n请输入医学问题> ").strip()
            if q == "" or q.lower() == "退出":
                break
            answer = await client.query(q)
            print("\nAI 回答：", answer)
    finally:
        await client.close()
        print(">>> 连接已关闭")

if __name__ == "__main__":
    asyncio.run(main())
