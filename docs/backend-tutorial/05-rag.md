# 05 一份 Markdown 怎样变成回答中的参考

主线：[knowledge_router.py](D:/Project/learnLittle/app/routers/knowledge_router.py) -> [knowledge_service.py](D:/Project/learnLittle/app/services/knowledge_service.py) -> [vector_store.py](D:/Project/learnLittle/app/rag/vector_store.py)。

## 任务 A：上传资料

路由先受限读取、检查扩展名和大小、算 MD5、检查当前用户重复文件。这些 preflight 错误发生在打开 SSE 之前，仍能返回普通 HTTP 错误。

通过后，`event_generator` 自己开数据库 session，让 `iter_save_document` 逐步执行：

```text
processing：保存文件
  -> processing：解析文本
  -> processing：切片
  -> processing：向量化 / 入 Chroma
  -> completed：服务函数完成并提供文档结果
  -> route commit
  -> finish：路由结束
```

`completed` 不是“SQL 已提交”的承诺；它先于 route commit。这个时序与新聊天的 `done` 不同。

文件名由服务端安全生成，原名称供显示。`parse_document` 支持 PDF、MD、TXT；PDF 提取文本，不做扫描图片 OCR。解析或写向量失败时有清理文件的处理，但磁盘、SQL、Chroma 没有分布式事务，不能承诺所有取消或提交异常都完美补偿。

## 任务 B：切成片段

[TextSplitter](D:/Project/learnLittle/app/rag/text_splitter.py) 用的是字符数，而非 Token 数。Markdown 按一至四级标题组织章节；短段落合并，长段落再 `_window` 滑窗。overlap 主要出现在长段窗口，不是所有相邻片段都有统一重叠。

一个片段不仅有 content，还需要 user_id、document_id/note_id、chunk_index、section_title 等 metadata。正文帮助模型回答，metadata 用来过滤用户、展示来源和删除整份文档的切片。

知识文档存 rag collection，笔记存 notes collection。笔记也切片，长笔记不是只有一个向量。

## 任务 C：向量化

[embeddings.py](D:/Project/learnLittle/app/rag/embeddings.py) 的选择顺序：

```text
测试注入函数 > 配置的 embedding/LLM key 对应 API > 没有 key 时确定性哈希向量
```

有 key 但调用失败会抛错，不会静默把真向量换成哈希。哈希向量便于离线测试流程，不等于语义嵌入模型。

`embed_texts` 按批次取未命中文本，用进程内 OrderedDict 做 TTL/LRU 缓存，再按原始次序组回结果。缓存 key 包含后端标签与文本摘要，不含 user_id，也不包含所有可能影响模型输出的 endpoint 信息，不能宣称端点完全隔离。

`upsert_chunks` 调 embedding 后检查维度，再写 Chroma。维度一致只保证形状兼容，同维度换模型仍可能让新旧语义空间不一致；不能只改模型名就认为旧向量可直接复用。

## 任务 D：检索并重排

单 collection 的流程：

```text
query -> _candidate_k 扩大候选
      -> _vector_search（where user_id）
      -> 可选 _bm25_search（最多 bm25_max_docs）
      -> 可选 rrf_fuse
      -> _maybe_rerank -> top_k
```

双源 `search_both` 并行查知识库和笔记，各路先不重排，合并后再重排。开启 hybrid 时做 RRF，关闭时按 score 合并排序。BM25 基于本次取回的有限文档计算，不是外置全文搜索集群。

`tokenize` 对中文生成单字和双字，对英文按词。`bm25_scores` 用词频、逆文档频率、长度计算分数。`rrf_fuse` 根据名次 `1/(k+rank)` 合并，避免硬比两种原始分数。

[retriever.py](D:/Project/learnLittle/app/rag/retriever.py) 优先注入重排函数，其次 CrossEncoder，最后词覆盖率。模型适配支持 `predict` 和 `compute_score`；默认不下载，加载失败会记住失败状态并回退。重排执行报错则保留输入顺序。`score` 会被不同阶段覆盖，不是统一校准的“正确概率”。

## 任务 E：决定要不要 RAG，再压缩参考

`decide_retrieval` 比当前用户两个 collection 的最小 Top-1 距离与阈值。距离大则跳过，距离小则检索；评分异常则放行检索。外层新聊天 `_retrieve` 还有总超时，整体失败会降级为无 RAG 继续 Agent，两层失败策略不要混淆。

主聊天默认拿当前问题检索，`chat_hyde_enabled=False`。打开该开关后，还需 `hyde_enabled` 才生成假设答案作为召回查询；重排仍用原问题。HyDE 缓存按模型、用户和问题划分，失败回原句，假设答案本身不是可信证据。

`summarize_hits` 并发处理命中副本，用压缩内容拼提示，保留原始 hits 供 sources 使用。虽然功能动机是“长切片摘要”，**当前 `_summarize_one` 对开启开关的非空切片都尝试摘要，并没有先比较一个长文本阈值**。关闭、没 key、空结果或失败时截断。知识库搜索接口不经过这层摘要，也不经过聊天 RAG 门控。

**练习**：命中原文和模型实际看到的参考为何不同？因为 sources 保留原命中，提示使用摘要副本。
