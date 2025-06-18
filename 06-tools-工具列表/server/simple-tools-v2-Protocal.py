import asyncio
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server

app = Server("tools-server")

@app.list_tools()
async def list_tools() -> list[types.Tool]:
    """
    返回服务器提供的工具列表
    """
    return [
        types.Tool(
            name="calculator",
            description="执行基本的数学运算（加、减、乘、除）",
            inputSchema={
                "type": "object",
                "properties": {
                    "operation": {
                        "type": "string",
                        "enum": ["add", "subtract", "multiply", "divide"]
                    },
                    "a": {"type": "number"},
                    "b": {"type": "number"}
                },
                "required": ["operation", "a", "b"]
            }
        ),
        types.Tool(
            name="text_analyzer",
            description="分析文本，统计字符数和单词数",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string"}
                },
                "required": ["text"]
            }
        )
    ]

@app.call_tool()
async def call_tool(
    name: str,
    arguments: dict
) -> list[types.TextContent]:
    """
    处理工具调用请求
    """
    if name == "calculator":
        operation = arguments["operation"]
        a = arguments["a"]
        b = arguments["b"]
        
        if operation == "add":
            result = a + b
        elif operation == "subtract":
            result = a - b
        elif operation == "multiply":
            result = a * b
        elif operation == "divide":
            if b == 0:
                return [types.TextContent(type="text", text="错误：除数不能为零")]
            result = a / b
            
        return [types.TextContent(type="text", text=f"计算结果: {result}")]
    
    elif name == "text_analyzer":
        text = arguments["text"]
        char_count = len(text)
        word_count = len(text.split())
        
        return [types.TextContent(
            type="text", 
            text=f"字符数: {char_count}\n单词数: {word_count}"
        )]
    
    return [types.TextContent(type="text", text=f"未知工具: {name}")]

async def main():
    async with stdio_server() as streams:
        await app.run(
            streams[0],
            streams[1],
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main()) 