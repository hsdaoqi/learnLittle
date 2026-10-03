# 后端教程覆盖报告

源代码快照日期：2026-10-02。报告由静态 AST 与人工说明映射生成，不启动应用。

- Python 文件：107。
- 显式函数定义：702，其中命名函数/方法/嵌套函数 679，lambda 23。
- 独立函数解释及锚点：702；缺失：0；陈旧映射：0。
- test_* 定义：70；参数化执行数另算，未在本轮重新执行业务测试。
- 全部文件 SHA256 已与清单核对；AST 本身重新扫描以发现新增/删除文件。
- 文档覆盖率不等于测试覆盖率，也不代表所有外部服务集成已验证。

## 说明来源

- 按精确返回式说明：9。
- 简单注入槽的 AST 校验说明：30。
- 迁移逐项说明：20。
- 逐项人工说明：643。

所有非通用业务函数及测试/辅助函数有逐项人工说明；通用注入槽只有在 AST 符合单全局赋值/单返回模式时才采用精确模式说明。没有以 TODO、仅列函数名或原 docstring 凑覆盖。

## 检查命令

```powershell
Set-Location D:\Project\learnLittle
.\.venv\Scripts\python.exe docs\backend-tutorial\tools\build.py --check
```

检查失败时，先审读改变的源函数并更新 tools/notes.py 和任务章，再执行：

```powershell
.\.venv\Scripts\python.exe docs\backend-tutorial\tools\inventory.py
.\.venv\Scripts\python.exe docs\backend-tutorial\tools\build.py
.\.venv\Scripts\python.exe docs\backend-tutorial\tools\build.py --check
```

检查器验证当前源码与 inventory 一致、每个函数有解释、每个解释有对应定义、生成文档内容一致、教程内本地文件/显式锚点链接有效。人工语义准确性仍需审读，不能由覆盖数字替代。

## 每文件快照

| 文件 | 函数数 | SHA256 |
| --- | ---: | --- |
| `alembic/env.py` | 4 | `17c445ee7a3caebcdb1dde1d529a6770a155e551f751334525b5366fd95ea05e` |
| `alembic/versions/342a95208d0f_add_note_categories_and_notes_tables.py` | 2 | `5f40152a2bbde6a6f16113f85eb16cfb202a9833455f3643612ef9e4b85ff83b` |
| `alembic/versions/53816adf617f_add_review_records.py` | 2 | `c816a4fc8504f91a3b710a7c199edc8b11fc8ad6fdd6595606379afbefa4e843` |
| `alembic/versions/b7c1d4e8f901_add_knowledge_documents_table.py` | 2 | `d76b0a1d5a152c2e16cb644e5f2f298ff1a5dc2c0442228bb8c99693273a269b` |
| `alembic/versions/c3e9f2a7b890_add_model_traces_and_pricing.py` | 2 | `6058fd432f57a732ef3166a491aa49805de2819730effa22d0d5847826ed6454` |
| `alembic/versions/c8d2e5f0a123_add_chat_sessions_and_messages.py` | 2 | `0ed6511f5bae22ab658e740002a8cbe6bf5ac7c8b9b5e46447aae0c4e036a211` |
| `alembic/versions/d9e3f6a1b234_add_chat_summaries_table.py` | 2 | `eb291177a4bee29246761408da73d1fb901f846f2744c2adfe4bd6105a24de71` |
| `alembic/versions/e0f4a7b2c345_add_note_templates_and_fulltext.py` | 2 | `685991bf4371ef7e9bd5a0cb54c433a776c20e5c0a739d86b3ad12aa7121bd47` |
| `alembic/versions/e2aebef3f9e7_add_user_email_verrifie.py` | 2 | `1b878f821d376cf6f14919ffc7e584102b75c9b309616f13a76f24fe4a9c0827` |
| `alembic/versions/e471331632c9_initial_users_table.py` | 2 | `0ee37c7404fc6efcd2f07246f70643803c322ebc04a05073cbf8c3994de362ea` |
| `alembic/versions/f1a244c10001_chat_lifecycle.py` | 2 | `3622cf8b1d6ff5a8f7f57a26f40fc94da9a08f35733ce2a89dd3a66aa112c1ad` |
| `app/__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `app/ai_service/__init__.py` | 0 | `fe30c79bcbb3cde34eeabde2ea9166c31baed2af1ccb9581c1694ede5aff7fd6` |
| `app/ai_service/chat_graph.py` | 8 | `c8569a7c647f5ca48ec10bf89411910dba87ed2404d7e9cae4bbc978a5eebf37` |
| `app/ai_service/langchain_tools.py` | 4 | `2b89225a1990ecf3c1fce5d871216b043b98c5747a865a01165741b7fef379b6` |
| `app/ai_service/models.py` | 1 | `f86b802e7a499217959b9b49cba9b1dbc39410624e4f74bec006eec9cff9310c` |
| `app/ai_service/plan_execute.py` | 18 | `4b32ba64cbe163b003b5172257a419bd22f68d4f4bf55f7c29e3202069e5be29` |
| `app/ai_service/query_classifier.py` | 11 | `ad97ae63e9a33f8a6629bf2ada546dc0116dbd6ffa1bb8b17b702ff3d4f88ea4` |
| `app/ai_service/react_agent.py` | 11 | `dd85df3d450354c08710c2f5fbb6988e45b355e91cbd4a576ba3f929e3f875eb` |
| `app/ai_service/reflection.py` | 10 | `2c81375df780ca500b52bcc4fb0a240df7aae1a85a8a78313951a3d414cda8f1` |
| `app/ai_service/review_tools.py` | 2 | `7801b209090b52acfca437b6e7f6670c9ce53188a6255154eaa526e993e3d980` |
| `app/ai_service/runner.py` | 6 | `fe67cdddf6dc6b55609ca7127ab8cc7190c6b6b65448e08d92d34437f8a20bd5` |
| `app/ai_service/sse_slot.py` | 2 | `a9389a41d2be59ec6e3256b43c7ba4d9e3a6c1f66a07a3e94ad43200ab263a63` |
| `app/ai_service/thinking.py` | 7 | `6ab510b919e22d33f7cf3cd6cda3ce4a522ea9d96c0f90e7546e53e5a3a9ea83` |
| `app/ai_service/tool_registry.py` | 8 | `ee85ca91a5c886396ff658adf82fd40d9690a7a95a5af40930eca16bcb9515d1` |
| `app/ai_service/tools.py` | 16 | `8fb5c7315a7b8300a495c069f679451f2474335b7e6f8c7b542d8ed6b0a7940e` |
| `app/ai_service/usage_callback.py` | 4 | `70b94f4ccd08a0d215f9e0f3c557cd9996618eb12b3c1b3247ed9e8707bf404a` |
| `app/config.py` | 2 | `f958d4b624bd3c883a0c2b1b4037ecff3eb8a4c033a2e7e8a93ea00b974cb5a2` |
| `app/core/__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `app/core/after_commit.py` | 3 | `c6f1ac7430262331ded59360b7d528c8e5ddf2948fe5da46c328d16cbbdcf411` |
| `app/core/exception_handlers.py` | 4 | `660724862be86ade11315a3a2d7adb28c99199d3699e8649a1b31fbb59a84ab3` |
| `app/core/failed_response.py` | 2 | `bbbe262fac539490de29ce083240ea48bda5c2474f78bc2ff90791b714e1a4c0` |
| `app/core/rate_limit.py` | 6 | `de251105b9184c9e54ae89eee5dcccc7019e05a2fdc1379c72ab20809f981420` |
| `app/core/scheduler.py` | 5 | `56a4c617ee4459c71e4235650d3138e112f791d1795616e3494df3ea28cf0531` |
| `app/core/success_response.py` | 1 | `e62356f8b367b0cb86f712229ba5c8f974be96e3f8b42e45eb2d8a7a3428bb90` |
| `app/core/task_runner.py` | 4 | `d3d91094d4c5fde2e20d370411610e0e3cd585120deb065d97d9830f02a4a826` |
| `app/db/__init__.py` | 0 | `a220b6a3aa0b42f0fd959d960e5baa810777d4fd8aa3ac71c06944c67e02804f` |
| `app/db/database.py` | 5 | `c1f68ec22154160e45b68deb49d83c9d0efa25bd82b45afb780f88492587f43d` |
| `app/db/redis_client.py` | 6 | `48cf7df548f1a0040a132e277d419258924a3dd3a27ed46b018dadcddba08414` |
| `app/models/__init__.py` | 0 | `d03dcb27ec431c24a7211d9cbc3236c1a9a2322ca570dc645d391ecc137e79a0` |
| `app/models/base.py` | 0 | `e72efb5d72425781b1976b62eea36d0197eece02a49fe68f057bb6f61dfc2e53` |
| `app/models/category.py` | 2 | `8de90551b8484c6fdfd8a84b7f7c047c646c56009af51fa43b678492024622b0` |
| `app/models/chat.py` | 4 | `1ad96be6372981ed0b01e23528fac752140ceae0b4506b8967e898f0d702f278` |
| `app/models/knowledge.py` | 1 | `f839b0ec4fa599040781dcf13c13f8957d44eea36a60e58c1491b85d1bcfdf13` |
| `app/models/note.py` | 2 | `ed41210e1cfa5144eb24c51771cf4cf755a4ca8c5abba468e6cb19dfbf6c79a5` |
| `app/models/note_template.py` | 1 | `7ac2ab3a6cb57b34a01e563c0889b7f96a02b5797adf60f0b5edca2905c5cbba` |
| `app/models/review.py` | 1 | `0678ba47edc9820d1e45490c47164a99f1621114b0c66a1f051c17d87c3df833` |
| `app/models/usage.py` | 0 | `4053b16fe13e168cfbe870fcf5ee5c508eca10a9bc0ec5c40b5f42bad070009d` |
| `app/models/user.py` | 2 | `cebca68fc924a335811a0466f880426200d3edb3a377a1b511bd42fa3cde57b5` |
| `app/rag/__init__.py` | 0 | `937bf920360696face94271cbb966f3caeaab1ac4a23b758dad04f5e6d181bed` |
| `app/rag/chat_cache.py` | 12 | `abda5b0a9f02ce12a67ddb3e6bbe989a805ac397712fea63642d1920837a593e` |
| `app/rag/chat_history.py` | 3 | `56dfb099a481ad27c3ccc25470ff7749b465a908b0e67a456466b7195767b2e7` |
| `app/rag/document_parser.py` | 2 | `34fa8d7cd04c034f096409b723e872b12ab697ea1dc05063c986b8e3213a6b72` |
| `app/rag/embeddings.py` | 13 | `13997a372bd7069565668dcf4c0359e715d21c27f793be90b7ee7870449acadc` |
| `app/rag/hyde.py` | 7 | `1602087f94b9931074bc3a028701468ec5b0a3261e7b9e8be62903ca957c632f` |
| `app/rag/llm.py` | 1 | `7ae1b43a1c6848e31db7fea4223cf4ddef1c69078cf4d07662c154fd172cca81` |
| `app/rag/memory.py` | 9 | `c170ff2283e6e4f58be1cfcd9da6ea990f274d52e77c1340eacc2014f48a6672` |
| `app/rag/note_cards.py` | 4 | `33a1d42e362abf7da0593daf27da44ad34c93ff595adcede7446dfcc6fbf13d1` |
| `app/rag/rag_route.py` | 3 | `6d7668cd60d6eecd4f81c939068657b904c5a6275cf6fe9aa7772e554422c68c` |
| `app/rag/rag_summarize.py` | 8 | `b58ad327e89906e80f65db911c7239d2a46327b0b0c7e739dba5bf87cfbe6ed5` |
| `app/rag/retriever.py` | 19 | `2ea19e5dcab4f9a7d81ed66e3f230289ed53211bbbaf1e298122225ea211925a` |
| `app/rag/session_title.py` | 6 | `235de0f18c42559231477746fbf0d8ee273a5e5595dfb5ea3a69d9751f4074ba` |
| `app/rag/text_splitter.py` | 6 | `13a51a5d8bea2433905361e66bf09eeb5b60f204ed0b89ae8fbd6ac6ba2270db` |
| `app/rag/token_budget.py` | 4 | `46ca86ceb870c3d25c27c2af1a1e937d8be267e5ed179d72c6918009781d0730` |
| `app/rag/vector_store.py` | 22 | `c1de08bd9d563f62b561d7ad1fd4fb3b6bd6428f653849f340958ce02e61fc26` |
| `app/routers/__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `app/routers/category_router.py` | 10 | `24721500e0fa01f34f702957b3596c71dc2f49f65682a3ae6788510d4c8b9a10` |
| `app/routers/chat_router.py` | 5 | `4604ac5b8b49554fbadc68dd3db64e1a05de1b45cf98e7cecc5ef5329e04c641` |
| `app/routers/health.py` | 2 | `35f7ccf38bec3a37a098aff5eb4ef8a9e138f0340d292924e022cf37371c1dfe` |
| `app/routers/knowledge_router.py` | 6 | `f827652e5e69609a02eaa7cc824e79b5766b8c19ccbc3334b2480d2f1354a658` |
| `app/routers/note_router.py` | 15 | `5edfd1dbee5c6cfa534b5eba98167b2287f3cc4a6db8d9b521ba9634cecc09c7` |
| `app/routers/note_template_router.py` | 7 | `6f2ebaf0a687c080668c12f8af9cff6ad0b1396990f3454629225348bc7422eb` |
| `app/routers/review_router.py` | 3 | `6857d5e30708c4f58aca34d76196da5c536e55b5b5fe59fdc2a01ebaa4a90e64` |
| `app/routers/usage_router.py` | 1 | `813cf02c0d56e5e76f447eec88aac96998b18a706aa0d4a689dc4420d42f9ed1` |
| `app/routers/user.py` | 13 | `c33d99b161e5d692d080ef7ef3acc543a376f2ac274ecfbaf77aadab8fc7b446` |
| `app/schemas/__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `app/schemas/auth.py` | 6 | `6225630a49f8df617df4e48113d62d184153246d37cae05f2219e4e4d85fa839` |
| `app/schemas/category.py` | 1 | `2d4b8b03ccbbaa5d2a39314bdf879ebbfb0ad1a1ec93c71fdb564229ac38476e` |
| `app/schemas/chat.py` | 0 | `f3237553799e15755b45672c45726cd6025ae2ed141b3ac7af73ebb080e427c0` |
| `app/schemas/knowledge.py` | 0 | `47111c7ebc8de5ed3e320c9e56c1e3439682576fc2b1297518728bdb1a4da3d7` |
| `app/schemas/note.py` | 1 | `2f16497e1e6b6bcc46f22cb423fe5f9216af82c84f557ef674deee6d42305903` |
| `app/schemas/review.py` | 0 | `eb940f2dc8461375df214073dbf4bd110088a69364d766a1b5ff635ec620129e` |
| `app/schemas/template.py` | 0 | `9284491ea8dbbdb6e840f5a574b7036b57316e3976a8ea9b89fa75f89b055eea` |
| `app/services/__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `app/services/category_service.py` | 29 | `da32e1b1041038d7c73030d5dd54ad1e602d63c0eac8f5cda3f9d55002777bf1` |
| `app/services/chat_service.py` | 12 | `9dcf6f2d76d7fe03fa092577ae4bc6794352af5ed323016f7d63edfbaeeacb1d` |
| `app/services/email_service.py` | 12 | `08681736970ea8ffe25afa42b9e293bb89d5d42177b118f5c75fd8cd808c98d2` |
| `app/services/knowledge_service.py` | 10 | `36809c5b18acd3004f95839d56e48b630926b97a9c2ac28bf8319c060f0e0c48` |
| `app/services/note_ai_service.py` | 11 | `a6369bb3755447d768f3884f69cc0733b03a56fce07979275c28ab9b95b6a69e` |
| `app/services/note_service.py` | 22 | `3a99d47d3cf8ba7bb5457fafeaa3af29d901c86c5f92f8a0fa28693adbbc4212` |
| `app/services/note_template_service.py` | 8 | `98545ff7b9522e7092457772dabea63d61fce4900da0c81c6497ace28bb34c73` |
| `app/services/query_service.py` | 10 | `5885ffc6f12c95a7e1902d37fd581d6799c1bfb0813b44ec5995b1ee3fdce1a7` |
| `app/services/review_service.py` | 9 | `356441e0114e93cf0775b8e1f8bb5e6c979c548c557b8fe40e6d0d475cd14214` |
| `app/services/usage_service.py` | 14 | `af942bcf446e30e411b735c7572b4306bf5b7ebc46de39c3db40bd42e2fd403c` |
| `app/utils/__init__.py` | 0 | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `app/utils/auth_utils.py` | 38 | `14b37f216090e3270a640a32a2bc73b33fa1bababc50343a24899df3f456a841` |
| `app/utils/file_handler.py` | 8 | `e6d39a669a8748aa8e592a62c8f145e50a6c90ddb0ae794a347afc70e1efd32c` |
| `main.py` | 2 | `af83d0573b6be608db7ada289e8f81e7f77d129601cbf3836540161beb00bf85` |
| `tests/conftest.py` | 4 | `641445b25b6b3bf5f34a4e0f88f9d4d4b5752e31b54851fb8af4acff0ccefda7` |
| `tests/test_agent_alignment.py` | 42 | `3f12dfe97b417cde175ff64a7aadf6775bf340a9f6a252599aca0a108832236e` |
| `tests/test_chat_routes.py` | 12 | `5829e631898b628971d8fb7cfd9d12d427f7ffc11eabdd32100ab72e6c7201bd` |
| `tests/test_notes_categories.py` | 25 | `5968702bed1dbac36f8565ada342676ef84ee0746b817395b9d8c8e85892b55b` |
| `tests/test_persistence_alignment.py` | 7 | `e32631d4253d819a1b82db298f6d8db489ae2b788a39b6980456c0f55a3a79f6` |
| `tests/test_query_lifecycle.py` | 28 | `cf735c75acd4160e858f538c731e0b76d627590f2bb503c86983d35bb2f2ef9c` |
| `tests/test_retriever_predict.py` | 3 | `24acb52c086c5eedf12a5bdd7bae5af7d4305e45b670cf5befdc5c3308b7b825` |
| `tests/test_thinking.py` | 16 | `044246b03fff6f153ea46f00aaed591e7548394e845a42767b29148731025f88` |
| `tests/test_usage.py` | 8 | `60143a6101bddbf7bb92b1a1ec6cdbf40973e59ae6f6feb308a33eae0df1a239` |
