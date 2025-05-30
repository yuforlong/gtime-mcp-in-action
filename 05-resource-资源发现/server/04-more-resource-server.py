# server.py
import os, asyncio
from typing import Any, List
import faiss, numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

load_dotenv()

# 创建一个MCP服务器实例，名称为"rag-simple"
app = Server("rag-simple")

DOC_DIR = "/home/huangj2/Documents/mcp-in-action/05-resource-资源发现/server/medical_docs"

# 注册资源列表
@app.list_resources()
async def list_resources() -> list[types.Resource]:
    files = [f for f in os.listdir(DOC_DIR) if f.endswith(".txt")]
    return [
        types.Resource(
            uri=f"file://{os.path.join(DOC_DIR, fname)}",
            name=fname,
            description="医学文档",
            mimeType="text/plain"
        )
        for fname in files
    ]

# 读取资源内容
@app.read_resource()
async def read_resource(uri: str) -> str:
    path = uri.replace("file://", "")
    with open(path, encoding="utf-8") as f:
        return f.read()

# --- 以下为原有的 index_docs / retrieve_docs 工具逻辑（不注册为 tool，仅供本地调用） ---
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

async def index_docs(docs: List[str]) -> str:
    global _index, _docs
    emb = await embed_text(docs)
    _index.add(emb)
    _docs.extend(docs)
    return f"已索引 {len(docs)} 篇文档，总文档数：{len(_docs)}"

async def retrieve_docs(query: str, top_k: int = 3) -> str:
    q_emb = await embed_text([query])
    D, I = _index.search(q_emb, top_k)
    hits = [f"[{i}] {_docs[i]}" for i in I[0] if i < len(_docs)]
    return "\n\n".join(hits) or "未检索到相关文档。"

async def main():
    async with stdio_server() as streams:
        await app.run(
            streams[0],
            streams[1],
            app.create_initialization_options()
        )

if __name__ == "__main__":
    asyncio.run(main())
