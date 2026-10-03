# 04 用模板、写作建议和复习完成学习任务

## 任务 A：用模板创建笔记

入口：[note_template_service.py](D:/Project/learnLittle/app/services/note_template_service.py)。

模板把名称、分类文字、排序和 `content_structure` 存在 SQL，没有单独的 description 字段。这里模板的 category 是文字元数据，不是笔记的分类外键。

`body_from_structure` 按 `markdown`、`content`、`body` 优先级取正文。`apply_template` 加载当前用户模板，决定标题，然后调用普通 `note_service.create_note`，所以自动获得分类检查、回顾记录和提交后索引，而不是自己复制三套逻辑。

`create/list/get/update/delete_template` 负责用户隔离和模板 CRUD；路由 `_dump` 将 ORM 转为响应 Schema。删除模板不会自动删除已经套用它创建的笔记。

## 任务 B：让模型提出建议

入口：[note_ai_service.py](D:/Project/learnLittle/app/services/note_ai_service.py)。

```text
autocomplete / write_assist / suggest_tags
  -> 各自 build_*_prompt
  -> _complete：注入函数或兼容接口
  -> 返回建议字符串或标签列表
```

自动补全取光标前文本的前 1200 字和光标后前 400 字；这里“前 1200”不是取距离光标最近的末尾 1200。写作提示有 4000 字截取。`parse_tags` 处理模型输出，去重、限制五个、每个不超过 20 字。

这些函数返回建议，不会自动保存笔记或自动把 tags 写入数据库。真正接受建议后仍要走笔记更新接口。缺 key 或失败会返回空建议/列表，不会自动出现高质量离线模型。

测试使用 `set_note_ai_fn` 注入稳定返回，同时 `UsageTimer` 记录调用耗时和估算用量。

## 任务 C：今天复习，标记完成

入口：[review_service.py](D:/Project/learnLittle/app/services/review_service.py)。

`ensure_review_record` 在新笔记创建时建立记录，已有则返回已有项。`get_today_reviews` 连接活跃笔记筛选到期记录。`mark_reviewed` 检查所有权，再更新 review_count、quality、reviewed_at 和下次时间。

注意初始 interval 为 1 且立即到期；第一次完成会通过 `next_interval` 进入 **2 天**，不是“第一次完成后一律 1 天”。quality 目前只存储，不改变间隔算法，因此不能称为 SM-2 自适应算法。

`get_review_stats` 基于记录当前状态统计。每条记录只有最新 reviewed_at，不是每次打卡事件的独立日志，因此不能把它解读成完整历史学习轨迹。

同一能力还被 Agent 复用：

```text
today_reviews 闭包 -> get_today_reviews_tool -> format_today_reviews_text
mark_reviewed 闭包 -> mark_reviewed_tool -> complete_review_text
  -> mark_reviewed -> 工具自己的 commit
```

工具只是文本适配层，业务和权限仍在 service，不另造一套回顾规则。

## 任务 D：把笔记导出为邮件

`export_note_email` 先读取当前用户笔记，校验目标邮箱，再由 `note_attachment` 根据 MD/TXT 生成附件，`send_email` 构造 MIME 并发出。这已经是普通 HTTP 功能，但“Agent 的 send_email 工具”当前还没有注册，不要把两者混为一谈。

SMTP 支持测试注入；真实发送使用 `aiosmtplib`、STARTTLS 和连接异常重试，认证错误不会当作临时故障重复尝试。本地运行依赖清单没有列出 `aiosmtplib`，所以“别的接口可运行”不能证明新环境的邮件依赖齐全。

邮件发送不能与 SQL 组成原子事务，成功发出的信不可能靠数据库 rollback 收回。

**练习**：模板应用后为什么也会进入今日复习？因为它最终复用普通笔记创建，而不是直接写 Note 表。
