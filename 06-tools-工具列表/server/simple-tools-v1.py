import asyncio
from mcp.server.fastmcp import FastMCP
from mcp.server.stdio import stdio_server

# 初始化 FastMCP 服务器
mcp = FastMCP("tools-server")

@mcp.tool()
async def calculator(operation: str, a: float, b: float) -> str:
    """执行基本的数学运算
    Args:
        operation: 运算类型 (add, subtract, multiply, divide)
        a: 第一个数字
        b: 第二个数字
    """
    if operation == "add":
        return f"计算结果: {a + b}"
    elif operation == "subtract":
        return f"计算结果: {a - b}"
    elif operation == "multiply":
        return f"计算结果: {a * b}"
    elif operation == "divide":
        if b == 0:
            return "错误：除数不能为零"
        return f"计算结果: {a / b}"

@mcp.tool()
async def text_analyzer(text: str) -> str:
    """分析文本，统计字符数和单词数
    Args:
        text: 要分析的文本
    """
    char_count = len(text)
    word_count = len(text.split())
    return f"字符数: {char_count}\n单词数: {word_count}"

if __name__ == "__main__":
    mcp.run(transport="stdio") 