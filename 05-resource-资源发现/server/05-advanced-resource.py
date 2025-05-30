import asyncio
import os
import base64
from typing import Dict, List, Optional
import mcp.types as types
from mcp.server import Server
from mcp.server.stdio import stdio_server
from datetime import datetime

# 创建一个MCP服务器实例
app = Server("advanced-resource-server")

# 模拟资源存储
class ResourceStore:
    def __init__(self):
        self.resources: Dict[str, types.Resource] = {}
        self.subscribers: Dict[str, List[str]] = {}
        self.last_updated: Dict[str, datetime] = {}
    
    def add_resource(self, resource: types.Resource):
        self.resources[resource.uri] = resource
        self.last_updated[resource.uri] = datetime.now()
    
    def get_resource(self, uri: str) -> Optional[types.Resource]:
        return self.resources.get(uri)
    
    def subscribe(self, uri: str, client_id: str):
        if uri not in self.subscribers:
            self.subscribers[uri] = []
        if client_id not in self.subscribers[uri]:
            self.subscribers[uri].append(client_id)
    
    def unsubscribe(self, uri: str, client_id: str):
        if uri in self.subscribers:
            self.subscribers[uri].remove(client_id)
            if not self.subscribers[uri]:
                del self.subscribers[uri]

# 创建资源存储实例
resource_store = ResourceStore()

# 初始化一些示例资源
resource_store.add_resource(types.Resource(
    uri="file:///logs/system.log",
    name="System Logs",
    description="System log files containing application events",
    mimeType="text/plain"
))

resource_store.add_resource(types.Resource(
    uri="file:///images/logo.png",
    name="Company Logo",
    description="Company logo image in PNG format",
    mimeType="image/png"
))

# 资源列表处理函数
@app.list_resources()
async def list_resources() -> List[types.Resource]:
    return list(resource_store.resources.values())

# 资源模板处理函数
@app.list_resource_templates()
async def list_resource_templates() -> List[types.ResourceTemplate]:
    return [
        types.ResourceTemplate(
            uriTemplate="file:///logs/{log_name}.log",
            name="Log File Template",
            description="Template for accessing log files",
            mimeType="text/plain"
        ),
        types.ResourceTemplate(
            uriTemplate="file:///images/{image_name}.{format}",
            name="Image File Template",
            description="Template for accessing image files",
            mimeType="image/*"
        )
    ]

# 资源读取处理函数
@app.read_resource()
async def read_resource(uri: str) -> types.ResourceContents:
    resource = resource_store.get_resource(uri)
    if not resource:
        raise ValueError(f"Resource not found: {uri}")
    
    # 模拟读取资源内容
    if uri == "file:///logs/system.log":
        return types.ResourceContent(
            uri=uri,
            mimeType="text/plain",
            text="[INFO] System started at " + datetime.now().isoformat()
        )
    elif uri == "file:///images/logo.png":
        # 模拟二进制内容
        binary_data = b"PNG binary data..."  # 实际应用中这里应该是真实的图片数据
        return types.ResourceContent(
            uri=uri,
            mimeType="image/png",
            blob=base64.b64encode(binary_data).decode()
        )
    else:
        raise ValueError(f"Unsupported resource: {uri}")

# 资源订阅处理函数
@app.subscribe_resource()
async def subscribe_resource(uri: str, client_id: str):
    resource_store.subscribe(uri, client_id)
    return {"success": True}

# 资源取消订阅处理函数
@app.unsubscribe_resource()
async def unsubscribe_resource(uri: str, client_id: str):
    resource_store.unsubscribe(uri, client_id)
    return {"success": True}

# 模拟资源更新
async def simulate_resource_updates():
    while True:
        await asyncio.sleep(5)  # 每5秒更新一次
        for uri, subscribers in resource_store.subscribers.items():
            if subscribers:
                # 发送资源更新通知
                await app.send_notification(
                    "resources/updated",
                    {"uri": uri, "timestamp": datetime.now().isoformat()}
                )

async def main():
    # 启动资源更新模拟任务
    asyncio.create_task(simulate_resource_updates())
    
    # 启动服务器
    async with stdio_server() as streams:
        await app.run(
            streams[0],
            streams[1],
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main()) 