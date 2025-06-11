import sys
import asyncio
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from openai import OpenAI
import os
from dotenv import load_dotenv
import mcp.types as types

load_dotenv()

class CodeReviewClient:
    def __init__(self):
        self.session = None
        self.transport = None
        self.client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        self.prompts = None

    async def connect(self, server_script: str):
        # 1) 构造参数对象
        params = StdioServerParameters(
            command="/mnt/external_disk/venv/20250426_MCP_Server/bin/python",
            args=[server_script],
            cwd="../server"  # 设置工作目录为服务器目录
        )
        # 2) 保存上下文管理器
        self.transport = stdio_client(params)
        # 3) 进入上下文，拿到 stdio, write
        self.stdio, self.write = await self.transport.__aenter__()

        # 4) 初始化 MCP 会话
        self.session = await ClientSession(self.stdio, self.write).__aenter__()
        await self.session.initialize()
        
        # 5) 获取可用的提示模板
        self.prompts = await self.session.list_prompts()

        # 兼容 dict_items
        if not isinstance(self.prompts, dict):
            self.prompts = dict(self.prompts)

        prompt_list = self.prompts.get("prompts", [])

        print("可用提示模板：")
        for prompt in prompt_list:
            if hasattr(prompt, 'name') and hasattr(prompt, 'description'):
                print(f"- {prompt.name}: {prompt.description}")
            else:
                print(f"- 未知提示模板: {prompt}")

    async def use_prompt(self, prompt_name: str, arguments: dict[str, str]):
        # 获取提示内容
        prompt_result = await self.session.get_prompt(prompt_name, arguments)
        
        # 转换消息格式为 OpenAI API 所需的格式
        messages = []
        for msg in prompt_result.messages:
            if isinstance(msg.content, types.TextContent):
                messages.append({
                    "role": msg.role,
                    "content": msg.content.text
                })
        
        # 调用 LLM
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages
        )
        
        return response.choices[0].message.content

    async def close(self):
        if self.session:
            await self.session.__aexit__(None, None, None)
        if self.transport:
            await self.transport.__aexit__(None, None, None)

async def main():
    print(">>> 开始初始化代码审查系统")
    if len(sys.argv) < 2:
        print("用法: python client.py <server.py 路径>")
        return

    client = CodeReviewClient()
    try:
        await client.connect(sys.argv[1])
        print(">>> 系统连接成功")

        # 示例代码
        sample_code = """
            def calculate_fibonacci(n):
                if n <= 0:
                    return []
                elif n == 1:
                    return [0]
                fib = [0, 1]
                for i in range(2, n):
                    fib.append(fib[i-1] + fib[i-2])
                return fib
        """

        while True:
            print("\n请选择操作：")
            print("1. 代码审查")
            print("2. 代码解释")
            print("3. 退出")
            
            choice = input("> ")
            
            if choice == "3":
                break
                
            if choice == "1":
                print("\n请选择审查重点：")
                print("1. 性能")
                print("2. 安全性")
                print("3. 可读性")
                print("4. 综合")
                
                focus_choice = input("> ")
                focus_map = {
                    "1": "performance",
                    "2": "security",
                    "3": "readability",
                    "4": "general"
                }
                focus = focus_map.get(focus_choice, "general")
                
                print("\n正在审查代码...")
                response = await client.use_prompt("code-review", {
                    "code": sample_code,
                    "language": "Python",
                    "focus": focus
                })
                print("\n审查结果：\n", response)
                
            elif choice == "2":
                print("\n正在解释代码...")
                response = await client.use_prompt("explain-code", {
                    "code": sample_code,
                    "language": "Python"
                })
                print("\n解释：\n", response)

    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        await client.close()
        print(">>> 系统已关闭")

if __name__ == "__main__":
    asyncio.run(main()) 