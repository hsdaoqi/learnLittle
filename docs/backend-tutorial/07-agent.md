# 07 Agent 怎么查笔记、做计划和自检

## 任务 A：决定走一轮推理还是分步计划

[chat_graph.py](D:/Project/learnLittle/app/ai_service/chat_graph.py) 建一个 StateGraph：

```text
START -> classify -> react -> END
                  -> plan -> END
                          -> react（安全降级）
```

state 只保留 route，事件经过容量 128 的队列向外传递。内层 `classify/react/plan/forward/run` 都是实际函数，详解索引单独解释，不因藏在主函数内就忽略。

[query_classifier.py](D:/Project/learnLittle/app/ai_service/query_classifier.py) 先 L1 规则：复杂模式、多问题、多个工具意图、条件分支；问候或明确单工具意图可直接判简单。不确定才 L2 模型补全。解析失败、超时、没 key 默认 simple。

complex 但 Plan 不可用时 result.route 可以是 `plan_pending`；图只把 `plan_execute` 送入 plan，所以实际执行仍是 react，而不是存在一个等待队列。

## 任务 B：把 Python 函数变成模型可调用工具

[tool_registry.py](D:/Project/learnLittle/app/ai_service/tool_registry.py) 保存 ToolSpec：名称、描述、parameters、fn、group、parallel_safe。注册表是描述与实现的连接点，不是数据库审计表。

[tools.py](D:/Project/learnLittle/app/ai_service/tools.py) 的 `bind_user_tools` 生成当前用户闭包。模型可以传 `note_id`、query，但 user_id 来自服务端已经认证的外层。创建、更新、回顾完成工具自己开 session 和 commit；读取也有用户过滤。

搜索工具先向量召回多片段，回 SQL 确认活跃笔记和归属，按 note_id 去重，再生成保留 `(ID: ...)` 的卡片文本。没有可用卡片时关键词兜底。读取全文最多输出 20000 字。更新应先知道真实 ID，不能靠模型猜。

[langchain_tools.py](D:/Project/learnLittle/app/ai_service/langchain_tools.py) 把简单 JSON Schema 转 Pydantic 模型，再构造 StructuredTool。当前转换器主要覆盖 string/integer/number/boolean，不是完整 JSON Schema 解释器。可选 None 参数会被 `_run` 过滤，让 Python 默认值生效。

动态注册的 `spec.fn` 可以直接使用；否则从绑定的内置函数取实现。`read_only=True` 只提供 parallel_safe 工具。`groups_for` 在写工具组之外补充读笔记工具，允许先读后改。

## 任务 C：ReAct 循环

[react_agent.py](D:/Project/learnLittle/app/ai_service/react_agent.py)：

1. `build_react_system_prompt` 放行为要求、RAG 与用户引用。
2. `_history_messages` 把原有 user/assistant 角色变为 HumanMessage/AIMessage；摘要单独 SystemMessage。
3. `_create_chat_model` 设置兼容接口、流、超时、usage callback，模型 SDK 重试设为 0。
4. `_create_agent` 首选 LangChain `create_agent`，导入兼容路径可回到 LangGraph helper。
5. `astream_events(version="v2")` 不断产生模型/工具事件，`map_langchain_event` 转成应用协议。

`chunk_text` 提取正文；`chunk_reasoning` 提取接口给出的推理字段，两者事件不同。工具开始记录计数和开始时间，结束产生结果/耗时。连续工具调用超过六次触发循环保护，但仍先报告刚开始的工具，使上层写入保护不会漏掉它。模型输出正文会重置连续计数。

L2 修复最多做一次外层重跑，仅在启用且没有开始副作用/未知工具时允许。`parallel_safe` 与禁止重试名单共同判断，不是只看是否已经返回 tool_end。开始写操作后，即使没有结果，也要按“可能已执行”处理。

## 任务 D：执行一个有依赖的计划

例子：先搜索 -> 读取其中一篇 -> 总结。正确计划必须让读取步骤依赖搜索步骤拿到真实 note_id。

[plan_execute.py](D:/Project/learnLittle/app/ai_service/plan_execute.py)：

```text
generate_plan -> parse_plan_payload
  -> topological_batches 校验编号、未知依赖和环
  -> _safe_batches 拆只读并行/写入串行小批
  -> _execute_batch -> _execute_step
  -> build_synthesize_prompt -> 综合 -> L1 自检
```

计划中 `tool` 是步骤意图，不是把整个步骤机械转换成一次固定参数函数调用。`_execute_step` 把真实依赖结果放入任务，调用步骤 ReAct，让模型决定具体参数和读写顺序。工具为 none 的步骤做分析补全或无模型时保留依赖上下文。

无依赖只读步骤限量并行，写步骤串行。`_execute_batch.consume` 把子步骤事件放入队列，sentinel 表示某个子任务结束；退出时取消未完任务。它的队列与图的 maxsize=128 队列不是同一个对象。

规划、单步、综合、整轮有独立超时。失败且没有写操作可 `plan_fallback` 转 ReAct；写操作已经开始则返回需要核对状态的 error，不能整轮重放。提示词建议 2-5 步，解析器不靠提示词保证步数，运行层还检查最大步数。

## 任务 E：答案自检与替换

[reflection.py](D:/Project/learnLittle/app/ai_service/reflection.py) 的 L1 是答案质量增强，不是提交前强制审核。满足启用、答案长度、模型可用等条件才运行：

```text
yield reflection(checking) -> await critique
不通过：yield reflection(refining) -> await refine
yield stream_done(final)
```

先 yield 状态再等待，用户才看得到正在自检。批判异常/解析失败视为通过，修订失败保留草稿。ReAct 通过 `response_replace` 更新已展示草稿；Plan 一般先综合修订再输出完整 answer。两条执行路径都消费 `stream_l1_refine`，不再有收集全部事件后返回的兼容包装。

## 任务 F：模型角色与 thinking

[models.py](D:/Project/learnLittle/app/ai_service/models.py) 只拷贝 settings 并替换模型名。classifier/plan/reflection/title 可以分配不同 model，但共享 endpoint/key，不是多供应商路由。

[thinking.py](D:/Project/learnLittle/app/ai_service/thinking.py) 的 auto 只在匹配的 DashScope 地址加入 enable_thinking；其余不发送该扩展。主模型跟请求，分类/规划/批判跟各自配置。开启时相应 Agent 超时放宽。

attachment_ids 非空强制关闭主 thinking，目前只是互斥判断，不会读取附件、抽视频帧或调用视觉模型。不能因为 notice 写着视觉场景就认为视觉问答已实现。

**练习**：为什么“写入工具超时后再试一次”危险？超时只说明调用方没及时收到结果，不证明写入没有发生。
