'''
运行方式：
python 06-tools-工具列表/client/simple-client-v3.py 06-tools-工具列表/server/simple-tools-v1.py
此命令将启动客户端并连接到指定的工具服务器，然后根据用户输入动态调用工具
'''
import asyncio
import sys
import json
from mcp import ClientSession, StdioServerParameters
from mcp.types import Notification
from mcp.client.stdio import stdio_client

class ResultParser:
    @staticmethod
    def parse_calculator_result(result_text):
        """解析计算器结果"""
        try:
            # 从 "计算结果: 8.0" 中提取数字
            value = float(result_text.split(":")[1].strip())
            return {
                "type": "calculator",
                "value": value,
                "formatted": f"计算结果为: {value}"
            }
        except:
            return {
                "type": "calculator",
                "error": "无法解析计算结果",
                "raw": result_text
            }

    @staticmethod
    def parse_text_analyzer_result(result_text):
        """解析文本分析结果"""
        try:
            lines = result_text.split("\n")
            char_count = int(lines[0].split(":")[1].strip())
            word_count = int(lines[1].split(":")[1].strip())
            return {
                "type": "text_analyzer",
                "char_count": char_count,
                "word_count": word_count,
                "formatted": f"文本分析结果：\n- 字符数：{char_count}\n- 单词数：{word_count}"
            }
        except:
            return {
                "type": "text_analyzer",
                "error": "无法解析分析结果",
                "raw": result_text
            }

    @staticmethod
    def parse_result(tool_name, result_text):
        """根据工具类型选择解析方法"""
        if tool_name == "calculator":
            return ResultParser.parse_calculator_result(result_text)
        elif tool_name == "text_analyzer":
            return ResultParser.parse_text_analyzer_result(result_text)
        return {
            "type": "unknown",
            "raw": result_text
        }

class ToolSelector:
    def __init__(self, tools):
        self.tools = tools
        self.tool_descriptions = self._create_tool_descriptions()

    def _create_tool_descriptions(self):
        descriptions = []
        for tool in self.tools:
            desc = f"工具名称: {tool.name}\n"
            desc += f"描述: {tool.description}\n"
            desc += f"参数要求: {json.dumps(tool.inputSchema, ensure_ascii=False, indent=2)}\n"
            descriptions.append(desc)
        return "\n".join(descriptions)

    def select_tool(self, user_input):
        # 这里可以集成LLM来选择最合适的工具
        # 简化版本：根据关键词匹配
        user_input = user_input.lower()
        
        for tool in self.tools:
            if tool.name == "calculator" and any(word in user_input for word in ["计算", "加", "减", "乘", "除"]):
                return self._prepare_calculator_args(user_input)
            elif tool.name == "text_analyzer" and any(word in user_input for word in ["分析", "统计", "字数", "字符"]):
                return self._prepare_text_analyzer_args(user_input)
        
        return None, None

    def _prepare_calculator_args(self, user_input):
        # 简化版本：固定使用加法
        # 实际应用中可以使用LLM来解析用户输入
        return "calculator", {
            "operation": "add",
            "a": 5,
            "b": 3
        }

    def _prepare_text_analyzer_args(self, user_input):
        # 简化版本：使用用户输入作为文本
        return "text_analyzer", {
            "text": user_input
        }

async def main():
    if len(sys.argv) < 2:
        print("Usage: python simple_client_v3.py <path_to_server_script>")
        sys.exit(1)

    server_script = sys.argv[1]
    params = StdioServerParameters(
        command="/mnt/external_disk/venv/20250426_MCP_Server/bin/python3",
        args=[server_script],
        env=None
    )

    async with stdio_client(params) as (reader, writer):
        async with ClientSession(reader, writer) as session:
            # 初始化握手
            await session.initialize()
            
            # 发送初始化完成通知
            notification = Notification(
                method="notifications/initialized",
                params={}
            )
            await session.send_notification(notification)

            # 获取工具列表
            response = await session.list_tools()
            tool_selector = ToolSelector(response.tools)

            print("欢迎使用工具调用系统！")
            print("可用工具列表：")
            print(tool_selector.tool_descriptions)
            print("\n请输入您的需求（输入'退出'结束）：")

            while True:
                user_input = input("> ")
                if user_input.lower() == "退出":
                    break

                tool_name, arguments = tool_selector.select_tool(user_input)
                if tool_name is None:
                    print("抱歉，没有找到合适的工具来处理您的需求。")
                    print("请尝试使用以下关键词：")
                    print("- 计算/加/减/乘/除：使用计算器")
                    print("- 分析/统计/字数：使用文本分析器")
                    continue

                try:
                    result = await session.call_tool(tool_name, arguments)
                    result_text = result.content[0].text
                    
                    # 使用ResultParser解析结果
                    parsed_result = ResultParser.parse_result(tool_name, result_text)
                    
                    print(f"\n工具 '{tool_name}' 的执行结果：")
                    if "error" in parsed_result:
                        print(f"错误: {parsed_result['error']}")
                        print(f"原始输出: {parsed_result['raw']}")
                    else:
                        print(parsed_result["formatted"])
                        
                    # 如果需要，可以访问解析后的结构化数据
                    if tool_name == "calculator":
                        print(f"数值结果: {parsed_result['value']}")
                    elif tool_name == "text_analyzer":
                        print(f"详细统计: 字符数={parsed_result['char_count']}, 单词数={parsed_result['word_count']}")
                        
                except Exception as e:
                    print(f"调用工具时出错: {str(e)}")

                print("\n请输入新的需求（输入'退出'结束）：")

if __name__ == "__main__":
    asyncio.run(main()) 