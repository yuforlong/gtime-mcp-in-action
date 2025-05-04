# -*- coding: utf-8 -*-
"""
定义代理的任务管理器，负责处理接收到的任务请求。
"""
import sys
import os
import logging
import json
import datetime
# 移除 Starlette 导入，因为我们不再直接返回它
# from starlette.responses import JSONResponse

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,  # 设置为 DEBUG 级别以获取更多信息
    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# 获取脚本所在目录的绝对路径
script_dir = os.path.dirname(os.path.abspath(__file__))
# 获取父目录 (mcp-in-action or the directory containing A2A)
# 注意: 如果你的脚本在 src/my_project/ 下，可能需要再多一个 os.path.dirname
# 假设脚本就在 21-a2a-hello-world 下，A2A 在上一级
parent_dir = os.path.dirname(script_dir)
# 将包含 A2A 的目录添加到 sys.path 的开头
sys.path.insert(0, parent_dir)
# --- End: sys.path modification ---

from typing import AsyncIterable

# 导入 A2A 库中的类型
from A2A.samples.python.common.server.task_manager import InMemoryTaskManager
from A2A.samples.python.common.server.utils import new_not_implemented_error
from A2A.samples.python.common.types import (
    Artifact,
    JSONRPCResponse, # 保留类型提示
    Message,
    SendTaskRequest,
    SendTaskResponse, # 我们需要返回这个类型
    SendTaskStreamingRequest,
    SendTaskStreamingResponse,
    Task,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
    InternalError,
    TextPart,
)

class MyAgentTaskManager(InMemoryTaskManager):
  """
  自定义的任务管理器，继承自内存任务管理器。
  这个简单的实现只处理 on_send_task 请求，执行回显并立即完成任务。
  (参考 google_adk/task_manager.py 模式)
  """
  def __init__(self):
    """初始化父类"""
    super().__init__()

  async def on_send_task(self, request: SendTaskRequest) -> SendTaskResponse:
    """
    处理一次性的 'send_task' 请求。

    Args:
      request: 包含任务详情的请求对象。

    Returns:
      包含任务最终状态和代理响应的 SendTaskResponse 对象。
    """
    try:
      # 1. 确保任务存在于存储中 (或创建)
      await self.upsert_task(request.params)

      task_id = request.params.id
      task_send_params = request.params # 方便访问
      
      # 2. 获取用户输入 (参考 _get_user_query)
      message = task_send_params.message
      if not message or not message.parts:
          raise ValueError("Invalid message format: missing parts")
      
      # --- Debugging Start ---
      logger.debug(f"Type of message.parts: {type(message.parts)}")
      logger.debug(f"Content of message.parts: {message.parts}")
      for i, part in enumerate(message.parts):
          logger.debug(f"Part {i}: type={type(part)}, value={part}")
      # --- Debugging End ---
      
      # 恢复检查 TextPart 实例
      text_part = next((part for part in message.parts if isinstance(part, TextPart)), None)
      if not text_part:
          # 更详细的错误信息
          logger.error(f"Failed to find TextPart instance in message.parts: {message.parts}")
          raise ValueError(f"No TextPart instance found in message parts")
      received_text = text_part.text # 现在应该可以直接访问 .text
      if not received_text:
          # 应该不太可能发生，因为 Pydantic 会验证
          raise ValueError("Empty text content in TextPart instance")

      # --- Echo Logic Start ---
      response_text = f"Echo: {received_text}"
      response_parts = [TextPart(type="text", text=response_text)]
      # 对于简单 echo，我们总是完成
      task_state = TaskState.COMPLETED 
      # 创建最终状态
      final_status = TaskStatus(
          state=task_state,
          # 在完成状态下，消息通常是可选的或为空，因为结果在 artifact 中
          # message=Message(role="agent", parts=response_parts) 
      )
      # 创建最终 artifact
      final_artifact = Artifact(parts=response_parts)
      # --- Echo Logic End ---

      # 3. 更新存储中的任务状态和 artifact (参考 _invoke 和 _update_store)
      # 使用 update_store 更新状态和 artifact
      updated_task = await self.update_store(
          task_id,
          final_status, # 传递最终状态
          [final_artifact] # 传递最终 artifact 列表
      )

      # 4. 直接返回包含更新后 Task 对象的 SendTaskResponse (关键点)
      # 不再调用 append_task_history 或 model_dump
      return SendTaskResponse(id=request.id, result=updated_task)
      
    except Exception as e:
      logger.error(f"Error processing send_task request: {str(e)}", exc_info=True)
      # 返回包含 Pydantic 错误对象的 SendTaskResponse
      return SendTaskResponse(id=request.id, error=InternalError(message=str(e)))

  async def on_send_task_subscribe(
    self,
    request: SendTaskStreamingRequest
  ) -> AsyncIterable[SendTaskStreamingResponse] | JSONRPCResponse:
    """
    处理订阅式的 'send_task_subscribe' 请求。
    在这个简单的示例中，我们不实现订阅逻辑，返回不支持的错误。

    Args:
      request: 订阅请求对象。

    Returns:
      JSONRPCResponse 错误，表示不支持此操作。
    """
    logger.warning("Streaming tasks are not supported in this implementation")
    return new_not_implemented_error(request.id)