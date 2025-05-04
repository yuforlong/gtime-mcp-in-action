# 导入必要的库
import asyncio  # 用于异步编程
import mcp.types as types  # 导入MCP类型定义
from mcp.server import Server  # 导入MCP服务器类
from mcp.server.stdio import stdio_server  # 导入标准输入输出服务器

# 创建一个MCP服务器实例，名称为"example-server"
app = Server("example-server")

# 使用装饰器注册资源列表处理函数
@app.list_resources()
async def list_resources() -> list[types.Resource]:
    """
    实现资源列表API，返回服务器提供的资源列表
    
    返回:
        list[types.Resource]: 资源对象列表
    """
    return [
        # 创建一个资源对象
        types.Resource(
            uri="example://resource",  # 资源的唯一标识符
            name="Example Resource"    # 资源的显示名称
        )
    ]

async def main():
    """
    主函数，启动MCP服务器
    """
    # 使用stdio_server上下文管理器获取标准输入输出流
    async with stdio_server() as streams:
        # 运行服务器，传入输入流、输出流和初始化选项
        await app.run(
            streams[0],  # 标准输入流
            streams[1],  # 标准输出流
            app.create_initialization_options()  # 创建默认初始化选项
        )

# 程序入口点
if __name__ == "__main__":
    # 运行异步主函数
    asyncio.run(main())