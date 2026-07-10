import ast
from typing import Any, List

from llm_client import HelloAgentsLLM

PLANNER_PROMPT_TEMPLATE = """
你是一个顶级的AI规划专家。你的任务是将用户提出的复杂问题分解成一个由多个简单步骤组成的行动计划。
请确保计划中的每个步骤都是一个独立的、可执行的子任务，并且严格按照逻辑顺序排列。
你的输出必须是一个Python列表，其中每个元素都是一个描述子任务的字符串。

问题: {question}

请严格按照以下格式输出你的计划,```python与```作为前后缀是必要的:
```python
["步骤1", "步骤2", "步骤3", ...]
```
"""

class Planner:
    def __init__(self, llm_client: HelloAgentsLLM):
        self.llm_client = llm_client
    def plan(self, question: str) -> list[str]:
        """
        为问题生成一个行动计划。
        """
        prompt = PLANNER_PROMPT_TEMPLATE.format(question=question)
        print("--- 正在生成计划 ---")
        resp = self.llm_client.think([{"role": "user", "content": prompt}]) or ""
        print(f"✅ 计划已生成:\n{resp}")

        try:
            # 找到```python和```之间的内容
            plan_str = resp.split("```python")[1].split("```")[0].strip()
            # 使用ast.literal_eval来安全地执行字符串，将其转换为Python列表
            plan = ast.literal_eval(plan_str)
            return plan if isinstance(plan, list) else []
        except (ValueError, SyntaxError, IndexError) as e:
            print(f"❌ 解析计划时出错: {e}")
            print(f"原始响应: {resp}")
            return []
        except Exception as e:
            print(f"❌ 解析计划时发生未知错误: {e}")
            return []

EXECUTOR_PROMPT_TEMPLATE = """
你是一位顶级的AI执行专家。你的任务是严格按照给定的计划，一步步地解决问题。
你将收到原始问题、完整的计划、以及到目前为止已经完成的步骤和结果。
请你专注于解决“当前步骤”，并仅输出该步骤的最终答案，不要输出任何额外的解释或对话。

# 原始问题:
{question}

# 完整计划:
{plan}

# 历史步骤与结果:
{history}

# 当前步骤:
{current_step}

请仅输出针对“当前步骤”的回答:
"""

class Executor:
    def __init__(self, llm_client):
        self.llm_client = llm_client  
    
    def execute(self, question:str, plan:list[str], history:list[str]) -> str:
        """
        执行行动计划，直到完成所有步骤。
        """
        history = ""
        for i, step in enumerate(plan):
            print(f"\n-> 正在执行步骤 {i+1}/{len(plan)}: {step}")
            prompt = EXECUTOR_PROMPT_TEMPLATE.format(question=question, plan=plan, history=history if history else "无", current_step=step)
            resp = self.llm_client.think([{"role": "user", "content": prompt}]) or ""
            print(f"✅ 执行结果已生成:\n{resp}")
            history += f"步骤 {i+1}: {step}\n结果: {resp}\n\n"
        # 循环结束后，最后一步的响应就是最终答案
        final_answer = resp if 'resp' in locals() else "无结果"
        return final_answer 

class PlanSolve:
    def __init__(self, llm_client: HelloAgentsLLM):
        self.llm_client = llm_client
        self.planner = Planner(llm_client)
        self.executor = Executor(llm_client)
    def run(self, question: str) -> str:
        """
        为问题生成一个行动计划，然后执行该计划。
        """
        print(f"\n--- 开始处理问题 ---\n问题: {question}")
        plan = self.planner.plan(question)
        if not plan:
            print("\n--- 任务终止 --- \n无法生成有效的行动计划。")
            return "无法生成计划"
        final_answer = self.executor.execute(question, plan, [])
        # 为了能够在 PlanSolve 的 run 方法中打印出 final_answer，我们可以这样处理
        # 因为 execute 方法返回的就是 final_answer，我们可以直接打印出来
        print(f"\n--- 任务完成 ---\n最终答案: {final_answer}")
        return final_answer

if __name__ == '__main__':
    try:
        llmClient = HelloAgentsLLM()
        planSolve = PlanSolve(llmClient)
        question = "一个水果店周一卖出了15个苹果。周二卖出的苹果数量是周一的两倍。周三卖出的数量比周二少了5个。请问这三天总共卖出了多少个苹果？"
        final_answer = planSolve.run(question)
        print(final_answer)
    except Exception as e:
        print(f"❌ 运行时出错: {e}")