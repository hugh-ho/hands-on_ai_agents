# hands-on_ai_agents

1. plan_solve + react 实现
2. function calling  保证plan 和工具调用的稳定性
3. excution 需要最后一把汇总，返回最终答案
4. excution 是模型自己执行计算，不可靠，应该用脚本执行
5. 只有自我批评，没有执行/测试反馈。reflect 是"凭想象"评审——不跑代码、不验证。语法错/运行错/逻辑错全看不出来；"无需改进"是模型声称，不是事实。Reflexion 论文的核心是 self-reflection + 环境反馈（测试结果/执行 trace），这里只有一半。→ 

6. agent 实现流式和文件返回 同一个方法