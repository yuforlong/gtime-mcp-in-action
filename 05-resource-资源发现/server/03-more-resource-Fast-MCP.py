# server.py
import os, asyncio
from typing import Any, List
import faiss, numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from mcp.server.fastmcp import FastMCP
import mcp.types as types

load_dotenv()

# 指定文档目录，服务器启动时，会将该目录下所有 .txt 文件暴露为资源
DOC_DIR = "/home/huangj2/Documents/mcp-in-action/05-resource-资源发现/server/medical_docs"

# 启动 FastMCP，并开启 resources 能力
mcp = FastMCP(
    server_name="rag",
    version="1.0.0",
    capabilities={"resources": {}}
)

# 动态注册每个 txt 文件为资源（用闭包捕获 path，函数无参数）
def make_resource(path, fname):
    @mcp.resource(f"file://{path}", name=fname, description="医学文档", mime_type="text/plain")
    async def resource_func():
        with open(path, encoding="utf-8") as f:
            return f.read()
    return resource_func

for fname in os.listdir(DOC_DIR):
    if fname.endswith(".txt"):
        path = os.path.join(DOC_DIR, fname)
        make_resource(path, fname)

# 2) 读取资源内容（可选，已由 @mcp.resource 处理，可保留或删除）
# @mcp.read_resource()
# async def read_resource(uri: Any) -> list[types.ResourceContents]:
#     path = uri.replace("file://", "")
#     text = open(path, encoding="utf-8").read()
#     return [
#         types.ResourceContents(
#             uri=uri,
#             mimeType="text/plain",
#             text=text
#         )
#     ]

# --- 以下保留原有的 index_docs / retrieve_docs 工具 ---
_index = faiss.IndexFlatL2(1536)
_docs: List[str] = []
openai = OpenAI()

async def embed_text(texts: List[str]) -> np.ndarray:
    resp = openai.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
        encoding_format="float"
    )
    return np.array([d.embedding for d in resp.data], dtype="float32")

@mcp.tool()
async def index_docs(docs: List[str]) -> str:
    global _index, _docs
    emb = await embed_text(docs)
    _index.add(emb)
    _docs.extend(docs)
    return f"已索引 {len(docs)} 篇文档，总文档数：{len(_docs)}"

@mcp.tool()
async def retrieve_docs(query: str, top_k: int = 3) -> str:
    q_emb = await embed_text([query])
    D, I = _index.search(q_emb, top_k)
    hits = [f"[{i}] {_docs[i]}" for i in I[0] if i < len(_docs)]
    return "\n\n".join(hits) or "未检索到相关文档。"

if __name__ == "__main__":
    # stdio transport
    mcp.run(transport="stdio")
