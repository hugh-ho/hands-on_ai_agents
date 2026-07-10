from locale import THOUSEP
import re
"""
ReAct 智能体示例。

本模块由 react.ipynb 整理而来，包含：
1. HelloAgentsLLM：兼容 OpenAI 接口的 LLM 客户端
2. search：基于 SerpApi 的网页搜索工具
3. ToolExecutor：工具执行器
"""

import os
from openai import OpenAI
from dotenv import load_dotenv
from typing import List, Dict, Any
from serpapi import SerpApiClient

# 加载 .env 文件中的环境变量
load_dotenv()


# ============================================================
# 一、LLM 客户端
# 为了让代码结构更清晰、更易于复用，我们来定义一个专属的LLM客户端类。
# 这个类将封装所有与模型服务交互的细节，让我们的主逻辑可以更专注于智能体的构建。
# ============================================================
class HelloAgentsLLM:
    """
    为本书 "Hello Agents" 定制的LLM客户端。
    它用于调用任何兼容OpenAI接口的服务，并默认使用流式响应。
    """
    def __init__(self, model: str = None, apiKey: str = None, baseUrl: str = None, timeout: int = None):
        """
        初始化客户端。优先使用传入参数，如果未提供，则从环境变量加载。
        """
        self.model = model or os.getenv("LLM_MODEL_ID")
        apiKey = apiKey or os.getenv("LLM_API_KEY")
        baseUrl = baseUrl or os.getenv("LLM_BASE_URL")
        timeout = timeout or int(os.getenv("LLM_TIMEOUT", 60))

        if not all([self.model, apiKey, baseUrl]):
            raise ValueError("模型ID、API密钥和服务地址必须被提供或在.env文件中定义。")

        self.client = OpenAI(api_key=apiKey, base_url=baseUrl, timeout=timeout)

    def think(self, messages: List[Dict[str, str]], temperature: float = 0) -> str:
        """
        调用大语言模型进行思考，并返回其响应。
        """
        print(f"🧠 正在调用 {self.model} 模型...")
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temperature,
                stream=True,
            )

            # 处理流式响应
            print("✅ 大语言模型响应成功:")
            collected_content = []
            for chunk in response:
                if not chunk.choices:
                    continue
                content = chunk.choices[0].delta.content or ""
                print(content, end="", flush=True)
                collected_content.append(content)
            print()  # 在流式输出结束后换行
            return "".join(collected_content)

        except Exception as e:
            print(f"❌ 调用LLM API时发生错误: {e}")
            return None


# ============================================================
# 二、构建工具的调用
# ============================================================
def search(query: str) -> str:
    """
    一个基于SerpApi的实战网页搜索引擎工具。
    它会智能地解析搜索结果，优先返回直接答案或知识图谱信息。
    """
    print(f"🔍 正在执行 [SerpApi] 网页搜索: {query}")
    try:
        api_key = os.getenv("SERPAPI_API_KEY")
        if not api_key:
            return "错误:SERPAPI_API_KEY 未在 .env 文件中配置。"

        params = {
            "engine": "google",
            "q": query,
            "api_key": api_key,
            "gl": "cn",  # 国家代码
            "hl": "zh-cn", # 语言代码
        }

        client = SerpApiClient(params)
        results = client.get_dict()

        # 智能解析:优先寻找最直接的答案
        if "answer_box_list" in results:
            return "\n".join(results["answer_box_list"])
        if "answer_box" in results and "answer" in results["answer_box"]:
            return results["answer_box"]["answer"]
        if "knowledge_graph" in results and "description" in results["knowledge_graph"]:
            return results["knowledge_graph"]["description"]
        if "organic_results" in results and results["organic_results"]:
            # 如果没有直接答案，则返回前三个有机结果的摘要
            snippets = [
                f"[{i+1}] {res.get('title', '')}\n{res.get('snippet', '')}"
                for i, res in enumerate(results["organic_results"][:3])
            ]
            return "\n\n".join(snippets)

        return f"对不起，没有找到关于 '{query}' 的信息。"

    except Exception as e:
        return f"搜索时发生错误: {e}"


# ============================================================
# 三、构建执行器
# ============================================================
class ToolExecutor:
    """
    一个工具执行器，负责管理和执行工具。
    """
    def __init__(self):
        self.tools: Dict[str, Dict[str, Any]] = {}

    def registerTool(self, name: str, description: str, func: callable):
        """
        向工具箱中注册一个新工具。
        """
        if name in self.tools:
            print(f"警告:工具 '{name}' 已存在，将被覆盖。")
        self.tools[name] = {"description": description, "func": func}
        print(f"工具 '{name}' 已注册。")

    def getTool(self, name: str) -> callable:
        """
        根据名称获取一个工具的执行函数。
        """
        return self.tools.get(name, {}).get("func")

    def getAvailableTools(self) -> str:
        """
        获取所有可用工具的格式化描述字符串。
        """
        return "\n".join([
            f"- {name}: {info['description']}"
            for name, info in self.tools.items()
        ])


# ============================================================
# 客户端使用示例
# ============================================================
def demo_llm() -> HelloAgentsLLM:
    try:
        llmClient = HelloAgentsLLM()

        exampleMessages = [
            {"role": "system", "content": "You are a helpful assistant that writes Python code."},
            {"role": "user", "content": "写一个快速排序算法"}
        ]

        print("--- 调用LLM ---")
        responseText = llmClient.think(exampleMessages)
        if responseText:
            print("\n\n--- 完整模型响应 ---")
            print(responseText)
            
        return llmClient

    except ValueError as e:
        print(e)
        return None


# ============================================================
# 工具初始化与使用示例
# ============================================================
def demo_tools() -> ToolExecutor:
    # 1. 初始化工具执行器
    toolExecutor = ToolExecutor()

    # 2. 注册我们的实战搜索工具
    search_description = "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
    toolExecutor.registerTool("Search", search_description, search)

    # 3. 打印可用的工具
    print("\n--- 可用的工具 ---")
    print(toolExecutor.getAvailableTools())

    # 4. 智能体的Action调用，这次我们问一个实时性的问题
    print("\n--- 执行 Action: Search['英伟达最新的GPU型号是什么'] ---")
    tool_name = "Search"
    tool_input = "英伟达最新的GPU型号是什么"

    tool_function = toolExecutor.getTool(tool_name)
    if tool_function:
        observation = tool_function(tool_input)
        print("--- 观察 (Observation) ---")
        print(observation)
    else:
        print(f"错误:未找到名为 '{tool_name}' 的工具。")
        
    return toolExecutor

# ReAct 提示词模板
REACT_PROMPT_TEMPLATE = """
请注意，你是一个有能力调用外部工具的智能助手。

可用工具如下:
{tools}

【重要规则】
1. 每一轮你只能输出一个 Thought 和一个 Action，输出完 Action 后必须立即停止。
2. 绝对不能自己编造 Observation——Observation 会由系统在下一轮返回给你。
3. 不要在一轮里输出多个 Action，也不要自己模拟多步对话。
4. Action 必须是以下两种格式之一:
   - `{{tool_name}}[{{tool_input}}]`:调用一个可用工具（tool_input 写在一行内）。
   - `Finish[最终答案]`:当你已收集到足够信息、能回答用户问题时使用。

请严格按照以下格式回应（每轮只输出下面这两行）:

Thought: <你的思考：分析、规划下一步>
Action: <工具名[输入] 或 Finish[最终答案]>

示例（单轮）:
Thought: 我需要先查英伟达的现任CEO。
Action: Search[英伟达 现任CEO]
（输出到这里就停下，等待系统返回 Observation）

现在，请开始解决以下问题:
Question: {question}
History: {history}
"""

class ReactAgent:
    def __init__(self, llm_client: HelloAgentsLLM, tool_executor: ToolExecutor, max_steps: int = 5):
        self.llm_client = llm_client
        self.tool_executor = tool_executor
        self.max_steps = max_steps
        self.history = []
    
    def run(self, question: str) -> str:
        """
        运行智能体，直到问题被完全解决。
        """
        self.history = []
        current_step = 0
        while current_step < self.max_steps:
            current_step += 1
            print(f"第 {current_step} 步")

            # 1. 构建prompt
            prompt = REACT_PROMPT_TEMPLATE.format(
                tools=self.tool_executor.getAvailableTools(),
                question=question,
                history="\n".join(self.history)
            )
            # print(f"第 {current_step} 步 的 prompt: {prompt}")

            #2. 调用LLM
            messages = [{"role": "system", "content": prompt}]
            resp = self.llm_client.think(messages)
            if not resp:
                break
            #解析LLM的输出
            thought, action = self._parse_output(resp)
            if thought:
                print(f"思考: {thought}")

            if not action:
                # 兜底：模型可能直接给了答案但没按 Finish[...] 包裹，别把对的答案丢掉
                if resp and resp.strip():
                    print("⚠️ 未解析到 Action，但模型已有输出，作为兜底答案返回。")
                    return resp.strip()
                print("警告:未能解析出有效的Action，流程终止。")
                break
            if action.startswith("Finish"):
                # Finish 指令：提取最终答案并结束（DOTALL 允许答案跨行，None 防御格式不合规）
                m = re.match(r"Finish\[(.*)\]", action, re.DOTALL)
                if not m:
                    print(f"警告: Finish 格式不正确，原 action: {action!r}")
                    break
                final_answer = m.group(1)
                print(f"🎉 最终答案: {final_answer}")
                return final_answer
            else:
                tool_name, tool_input = self._parse_action(action)
                if not tool_name or not tool_input:
                    print("警告:未能解析出有效的工具调用，流程终止。")
                    continue
            
            print(f"🎬 行动: {tool_name}[{tool_input}]")

            tool_function = self.tool_executor.getTool(tool_name)
            if not tool_function:
                observation = f"错误:未找到名为 '{tool_name}' 的工具。"
            else:
                observation = tool_function(tool_input)
                print(f"Observation: {observation}")

                self.history.append(f"Action: {action}")
                self.history.append(f"Observation: {observation}")

                # 循环结束
        print("已达到最大步数，流程终止。")
        return None

# 3. 解析响应
# (这些方法是 ReActAgent 类的一部分)
    def _parse_output(self, text: str):
        """解析LLM的输出，提取Thought和Action。
        """
        # Thought: 匹配到 Action: 或文本末尾
        thought_match = re.search(r"Thought:\s*(.*?)(?=\nAction:|$)", text, re.DOTALL)
        thought = thought_match.group(1).strip() if thought_match else None
        # 优先识别 Finish[...]（允许最终答案跨行，贪婪到最后一个 ]）
        finish_match = re.search(r"Finish\[(.*)\]", text, re.DOTALL)
        if finish_match:
            return thought, f"Finish[{finish_match.group(1)}]"
        # 普通工具调用：只取第一个 Action 行，避免模型一轮输出多段时把后面的 Observation 一起吞掉
        action_match = re.search(r"Action:\s*(.+)", text)  # 不加 DOTALL，只到换行
        action = action_match.group(1).strip() if action_match else None
        return thought, action

    def _parse_action(self, action_text: str):
        """解析Action字符串，提取工具名称和输入。
        """
        match = re.match(r"(\w+)\[(.*)\]", action_text, re.DOTALL)
        if match:
            return match.group(1), match.group(2)
        return None, None
def initToolExecutor() -> ToolExecutor:
    toolExecutor = ToolExecutor()
    search_description = "一个网页搜索引擎。当你需要回答关于时事、事实以及在你的知识库中找不到的信息时，应使用此工具。"
    toolExecutor.registerTool("Search", search_description, search)
    return toolExecutor

if __name__ == '__main__':
     # 实例化 Agent 并运行，复用上方初始化好的实例
    agent = ReactAgent(HelloAgentsLLM(), initToolExecutor())
    print(f" ！！智能体运行结果: {agent.run('英伟达现任 CEO 是谁，他的姓名是？？，他的年龄是多少？？，  本科毕业时间是？？，  本科毕业学校是？？ 那所大学所在的城市是？？？')}")
  
