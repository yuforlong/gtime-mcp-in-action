# -*- coding: utf-8 -*-
"""
定义代理的任务管理器，负责处理接收到的任务请求。
"""
import sys
import os

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

# 导入 A2A 库中的类型，注意我们使用修改 sys.path 后的路径
from A2A.samples.python.common.server.task_manager import InMemoryTaskManager
from A2A.samples.python.common.types import (
    Artifact,
    JSONRPCResponse,
    Message,
    SendTaskRequest,
    SendTaskResponse,
    SendTaskStreamingRequest,
    SendTaskStreamingResponse,
    Task,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent, # 虽然没直接用，但通常一起导入
)

class MyAgentTaskManager(InMemoryTaskManager):
  """
  自定义的任务管理器，继承自内存任务管理器。
  这个简单的实现只处理 on_send_task 请求，执行回显并立即完成任务。
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
      包含任务最终状态和代理响应的响应对象。
    """
    # 1. 使用父类方法将任务存储/更新到内存中的 self.tasks 字典
    await self.upsert_task(request.params)

    task_id = request.params.id # 获取任务ID
    
    # 2. 从请求中提取输入文本
    message = request.params.message
    if not message or not message.parts:
        raise ValueError("Invalid message format: missing parts")
    
    # 获取第一个文本部分
    text_part = next((part for part in message.parts if part.type == "text"), None)
    if not text_part:
        raise ValueError("No text part found in message")
    
    received_text = text_part.text

    # 3. 调用内部方法更新任务状态为完成，并设置响应文本
    task = await self._update_task(
      task_id=task_id,
      task_state=TaskState.COMPLETED, # 直接标记为完成
      response_text=f"on_send_task received: {received_text}" # 构造回显内容
    )

    # 4. 构建并返回 SendTaskResponse，包含请求ID和处理结果(更新后的 task)
    return SendTaskResponse(id=request.id, result=task)

  async def on_send_task_subscribe(
    self,
    request: SendTaskStreamingRequest
  ) -> AsyncIterable[SendTaskStreamingResponse] | JSONRPCResponse:
    """
    处理订阅式的 'send_task_subscribe' 请求。
    在这个简单的示例中，我们不实现订阅逻辑。
    可以返回一个错误或直接忽略。这里我们简单地 pass。

    Args:
      request: 订阅请求对象。

    Returns:
      对于不支持的情况，可以考虑返回 JSONRPCResponse 错误，或根据协议要求处理。
      这里简单地不实现任何功能。
    """
    # TODO: 如果需要支持订阅，在这里实现逻辑
    pass # 在本示例中不处理订阅

  async def _update_task(
    self,
    task_id: str,
    task_state: TaskState,
    response_text: str,
  ) -> Task:
    """
    内部辅助方法，用于更新内存中指定任务的状态和响应。

    Args:
      task_id: 要更新的任务的 ID。
      task_state: 新的任务状态。
      response_text: 代理响应的文本内容。

    Returns:
      更新后的任务对象。
    """
    # 从父类的 self.tasks 字典中获取任务对象
    task = self.tasks[task_id]

    # 构建代理响应的消息部分
    agent_response_parts = [
      {
        "type": "text",
        "text": response_text,
      }
    ]

    # 更新任务的状态 (TaskStatus)
    task.status = TaskStatus(
      state=task_state, # 设置新的状态 (例如 COMPLETED)
      message=Message( # 设置代理的响应消息
        role="agent", # 标记消息来源为代理
        parts=agent_response_parts, # 包含响应文本
      )
    )

    # 更新任务的产出物 (Artifacts)，通常与最终响应一致
    task.artifacts = [
      Artifact(
        parts=agent_response_parts,
      )
    ]

    # 返回更新后的任务对象
    return task