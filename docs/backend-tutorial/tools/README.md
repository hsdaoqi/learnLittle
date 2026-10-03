# 教程工具维护

这些文件只维护文档，不属于后端业务函数覆盖口径。它们不导入 `main` 或 `app`，不读真实 `.env`，不创建数据库/Redis/Chroma/模型客户端。

| 文件 | 作用 |
| --- | --- |
| [inventory.py](D:/Project/learnLittle/docs/backend-tutorial/tools/inventory.py) | AST 提取文件、类、函数、lambda、签名、源码、静态调用与文件 SHA256；`collect` 只读，`main` 写 inventory.json |
| [notes.py](D:/Project/learnLittle/docs/backend-tutorial/tools/notes.py) | 人工逐函数说明、lambda 解释、迁移行为说明；`put` 防止重复 key |
| [build.py](D:/Project/learnLittle/docs/backend-tutorial/tools/build.py) | 生成逐文件详解、结构清单、函数快查、解释映射与覆盖报告；缺说明或多余说明会失败 |
| [test_docs.py](D:/Project/learnLittle/docs/backend-tutorial/tools/test_docs.py) | 标准库 unittest，验证覆盖、缺项拒绝、坏链接与 AST 隔离；仅临时样例文件，无业务服务 |

人工编辑任务章节和 `notes.py`，不要直接改生成的 atlas；生成器重跑会覆盖生成文件，但不自动覆盖任务章节。

```powershell
Set-Location D:\Project\learnLittle
.\.venv\Scripts\python.exe docs\backend-tutorial\tools\test_docs.py
.\.venv\Scripts\python.exe docs\backend-tutorial\tools\build.py --check
```

`--check` 不写生成文档。出现 source inventory is stale 时，先审读源码变化，再更新解释与章节，最后重新运行 inventory、build、check。不要只刷新哈希便声称人工讲解已更新。

源码链接使用当前 `D:/Project/learnLittle` 绝对路径，适合本机点击；目录搬迁后应重新生成，并统一调整人工章节链接。
