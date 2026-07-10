from hello_agents import SimpleAgent, HelloAgentsLLM
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量
load_dotenv()

llm = HelloAgentsLLM()

agent = SimpleAgent(
    name="AI 助手",
    llm=llm,
    system_prompt="你是一个专业的助手，能够回答用户的问题。",
)

response = agent.run("你好！请介绍一下自己")
print(response)

response = agent.run("请帮我计算 2 + 3 * 4")
print(response)

print(f"历史消息数: {len(agent.get_history())}")
