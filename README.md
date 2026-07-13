# hands-on_ai_agents

## 环境准备 (uv)

本项目用 [uv](https://docs.astral.sh/uv/) 管理依赖和虚拟环境。

```bash
# 1. 安装 uv（已安装可跳过）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 创建虚拟环境并安装全部依赖（含 dev 组），生成 uv.lock
uv sync

# 3. 运行脚本（无需手动 activate）
uv run python framework/react.py
uv run python hello_agents/agents/test_simple_agent.py

# 4. Notebook：在 VS Code 里选择 .venv 的解释器即可；或注册内核
uv run python -m ipykernel install --user --name hands-on-ai-agents
```

依赖锁在 `uv.lock`，换机器只需 `uv sync` 即可还原一致环境。

### 环境变量 (.env)

项目通过 `python-dotenv` 从项目根目录的 `.env` 读取配置。`.env` 已在 `.gitignore` 中（含密钥，勿提交），首次使用请在根目录新建一个。`framework/`、`hello_agents/` 下的脚本运行时会自动 `load_dotenv()`。

| 变量 | 必填 | 说明 |
|------|:----:|------|
| `LLM_API_KEY` | ✅ | OpenAI 兼容服务的 API Key |
| `LLM_MODEL_ID` | ✅ | 模型名/ID，如 `Qwen/Qwen2.5-VL-72B-Instruct` |
| `LLM_BASE_URL` | ✅ | OpenAI 兼容接口的 base URL |
| `SERPAPI_API_KEY` | ⚠️ | 联网搜索（serpapi）工具需要；不用搜索可不配 |
| `LLM_TIMEOUT` | ❌ | 请求超时秒数，默认 `60` |
| `MODELSCOPE_API_KEY` | ❌ | 仅当 `MyLLM(provider="modelscope")` 时需要 |
| `DEBUG` | ❌ | `true`/`false`，默认 `false`（`Config.from_env` 读取） |
| `LOG_LEVEL` | ❌ | 日志级别，默认 `INFO` |
| `TEMPERATURE` | ❌ | 采样温度，默认 `0.7` |
| `MAX_TOKENS` | ❌ | 最大 token 数，默认不限 |

`.env` 示例（替换为你的真实值）：

```bash
LLM_API_KEY=sk-xxxx
LLM_MODEL_ID=Qwen/Qwen2.5-VL-72B-Instruct
LLM_BASE_URL=https://your-openai-compatible-endpoint/v1
SERPAPI_API_KEY=your-serpapi-key
```

---

## 开发笔记

1. plan_solve + react 实现
2. function calling  保证plan 和工具调用的稳定性
3. excution 需要最后一把汇总，返回最终答案
4. excution 是模型自己执行计算，不可靠，应该用脚本执行
5. 只有自我批评，没有执行/测试反馈。reflect 是"凭想象"评审——不跑代码、不验证。语法错/运行错/逻辑错全看不出来；"无需改进"是模型声称，不是事实。Reflexion 论文的核心是 self-reflection + 环境反馈（测试结果/执行 trace），这里只有一半。→ 

6. agent 实现流式和文件返回 同一个方法