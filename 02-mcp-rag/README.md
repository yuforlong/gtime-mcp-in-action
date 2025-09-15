# RAG 系统使用说明

## 环境变量设置

本系统需要设置以下环境变量：

1. `OPENAI_API_KEY` - 用于服务器端生成嵌入向量
2. `DEEPSEEK_API_KEY` - 用于客户端生成回答

### 设置方法

#### 方法一：在终端中设置（临时）

```bash
export OPENAI_API_KEY=your_openai_api_key_here
export DEEPSEEK_API_KEY=your_deepseek_api_key_here
```

#### 方法二：在.env文件中设置（推荐）

1. 在服务器目录创建.env文件

```bash
cd rag-server
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

2. 在客户端目录创建.env文件

```bash
cd rag-client
echo "DEEPSEEK_API_KEY=your_deepseek_api_key_here" > .env
```

## 运行系统

1. 确保已安装所有依赖

```bash
cd rag-server
uv pip install -e .

cd ../rag-client
uv pip install -e .
```

2. 运行客户端（会自动启动服务器）

```bash
cd rag-client
uv run client-v3-deepseek.py ../rag-server/server.py
```

## 常见问题

### OpenAI API密钥错误

如果遇到以下错误：

```
openai.OpenAIError: The api_key client option must be set either by passing api_key to the client or by setting the OPENAI_API_KEY environment variable
```

请确保已正确设置OPENAI_API_KEY环境变量，可以通过以下命令检查：

```bash
echo $OPENAI_API_KEY
```

如果输出为空，请按照上述方法设置环境变量。