# tests/test_notes_categories.py

[源码](D:/Project/learnLittle/tests/test_notes_categories.py) | [任务流程 10](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

隔离回归测试与测试替身。每个函数的具体输入场景/断言目的见下方；不把测试替身当生产实现。

## 本文件导航

- [_register_and_login](#fn-b61cb9c9e803d2ae)
- [_find](#fn-d29c24f997a6d139)
- [_tree](#fn-4754ca61f31d1b82)
- [test_register_seeds_template_tree](#fn-6d35ff1bc0130ea7)
- [test_create_category_and_same_name_conflict](#fn-3863f2657e2e5828)
- [test_create_category_depth_limit](#fn-47ae7974f1375a67)
- [test_rename_and_soft_delete_promotes_children](#fn-51841814bb241567)
- [test_move_category_rejects_cycle](#fn-e73b5d8dd03fba83)
- [test_note_crud_flow](#fn-35be00c3e38b1203)
- [test_note_keyword_filter](#fn-d21ec54f2da87df0)
- [test_note_trash_restore_permanent](#fn-d67713242f6e1310)
- [test_category_delete_unties_notes](#fn-38e060d1aab57fa0)
- [test_cross_user_isolation](#fn-cd5c5f0e99cb20f2)
- [test_pinned_note_sorts_first](#fn-c34b6f88721d9cad)
- [test_category_recycle_restore_ancestors](#fn-a7821ca859d7d7f1)
- [test_category_permanent_delete_and_cleanup](#fn-1d14b330d5f04952)
- [test_category_permanent_delete_and_cleanup._age_and_clean](#fn-af3a5e549e1de0a4)
- [test_category_reorder_and_merge](#fn-0545acad6423c329)
- [test_note_format_txt_and_move_category](#fn-e86e08191072b6d7)
- [test_note_batch_and_cleanup](#fn-11a7c1cfce0e86a5)
- [test_note_batch_and_cleanup._age_and_clean](#fn-a79986431c5e59ca)
- [test_note_keyword_search_title_outranks_content](#fn-b8912ea74cfafa79)
- [test_note_template_crud_apply_and_isolation](#fn-34cd3f09374e5a7d)
- [test_note_ai_assist_uses_injected_fn](#fn-4548c023d536ceac)
- [test_note_ai_assist_uses_injected_fn.fake_complete](#fn-ed3639e7b14ca328)
<a id="fn-b61cb9c9e803d2ae"></a>

## _register_and_login

源码：[L6](D:/Project/learnLittle/tests/test_notes_categories.py:6)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

在隔离 TestClient 中注册登录，返回带 access 的 headers。fixture 关闭强制邮箱，不能照抄为默认生产注册规则。

**输入与签名**

```python
def _register_and_login(client: TestClient, username: str) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'Authorization': f'Bearer {tokens['access_token']}'}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
client.post
client.post('/api/v1/auth/login', json={'username': username, 'password': 'passw0rd123'}).json
```

<a id="fn-d29c24f997a6d139"></a>

## _find

源码：[L14](D:/Project/learnLittle/tests/test_notes_categories.py:14)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

递归遍历响应 children 找指定名称，没找到 None。测试辅助树查找，不调用分类 service。

**输入与签名**

```python
def _find(nodes: list[dict], name: str) -> dict | None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return node
return hit
return None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_find
```

<a id="fn-4754ca61f31d1b82"></a>

## _tree

源码：[L24](D:/Project/learnLittle/tests/test_notes_categories.py:24)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

GET 分类树并取 data，减少用例重复响应拆包。错误处理由测试后续断言暴露。

**输入与签名**

```python
def _tree(client: TestClient, headers: dict) -> list[dict]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return client.get('/api/v1/category/tree', headers=headers).json()['data']
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
client.get('/api/v1/category/tree', headers=headers).json
client.get
```

<a id="fn-6d35ff1bc0130ea7"></a>

## test_register_seeds_template_tree

源码：[L30](D:/Project/learnLittle/tests/test_notes_categories.py:30)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

注册后断言顶级默认名称顺序、技术子项与三层节点存在。证明注册复用播种，不是前端硬编码树。

**输入与签名**

```python
def test_register_seeds_template_tree(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert top_names == ['工作', '学习', '技术', '生活', '闪念', '阅读', '三体', '其他']
assert [c['name'] for c in tech['children']] == ['Flutter', 'Java', 'Nodejs', 'Vue']
assert doc is not None and doc['parent_id'] is not None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_register_and_login
_tree
_find
```

<a id="fn-3863f2657e2e5828"></a>

## test_create_category_and_same_name_conflict

源码：[L47](D:/Project/learnLittle/tests/test_notes_categories.py:47)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

同父级创建后检查排序，再重复同名要求 409，其他父级同名允许。覆盖应用级同级唯一规则。

**输入与签名**

```python
def test_create_category_and_same_name_conflict(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert resp.status_code == 200
assert resp.json()['data']['parent_id'] == work['id']
assert resp.json()['data']['sort_order'] == 2
assert resp.status_code == 409
assert resp.json()['code'] == 40904
assert client.post('/api/v1/category', json={'name': '周报'}, headers=headers).status_code == 200
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_register_and_login
_find
_tree
client.post
resp.json
```

<a id="fn-47ae7974f1375a67"></a>

## test_create_category_depth_limit

源码：[L72](D:/Project/learnLittle/tests/test_notes_categories.py:72)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

在已有第三层下继续创建，要求 400/INVALID_PARAMETER。验证不能只按 parent 存在就接受。

**输入与签名**

```python
def test_create_category_depth_limit(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert resp.status_code == 400
assert resp.json()['code'] == 40003
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_register_and_login
_find
_tree
client.post
resp.json
```

<a id="fn-51841814bb241567"></a>

## test_rename_and_soft_delete_promotes_children

源码：[L83](D:/Project/learnLittle/tests/test_notes_categories.py:83)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

先改父名再软删，断言父消失、活跃孩子变顶级。固定当前不是级联软删整树的语义。

**输入与签名**

```python
def test_rename_and_soft_delete_promotes_children(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert resp.json()['data']['name'] == '上班'
assert client.delete(f'/api/v1/category/{work['id']}', headers=headers).status_code == 200
assert _find(tree, '上班') is None
assert promoted is not None and promoted['parent_id'] is None
assert _find(tree, '项目文档') is not None and _find(tree, '项目文档')['parent_id'] is None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_register_and_login
_tree
_find
client.put
resp.json
client.delete
```

<a id="fn-e73b5d8dd03fba83"></a>

## test_move_category_rejects_cycle

源码：[L103](D:/Project/learnLittle/tests/test_notes_categories.py:103)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

将祖先移动到后代下，要求拒绝。防止分类链成环后递归/展示异常。

**输入与签名**

```python
def test_move_category_rejects_cycle(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert resp.status_code == 400
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_register_and_login
_tree
_find
client.post
```

<a id="fn-35be00c3e38b1203"></a>

## test_note_crud_flow

源码：[L119](D:/Project/learnLittle/tests/test_notes_categories.py:119)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

创建分类笔记，检查列表/详情，再只改置顶和 category_id=null，检查未分类过滤。验证部分更新与 MD 默认格式。

**输入与签名**

```python
def test_note_crud_flow(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert created.status_code == 200
assert listed['total'] == 1
assert listed['items'][0]['title'] == 'FastAPI 学习笔记'
assert client.get('/api/v1/note', params={'category_id': tech['id']}, headers=headers).json()['data']['total'] == 1
assert detail['content'].startswith('# DI')
assert detail['format'] == 'md'
assert updated['is_pinned'] is True and updated['category_id'] is None
assert client.get('/api/v1/note', params={'uncategorized': True}, headers=headers).json()['data']['total'] == 1
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_register_and_login
_find
_tree
client.post
created.json
client.get('/api/v1/note', headers=headers).json
client.get
client.get('/api/v1/note', params={'category_id': tech['id']}, headers=headers).json
client.get(f'/api/v1/note/{note_id}', headers=headers).json
detail['content'].startswith
client.put(f'/api/v1/note/{note_id}', json={'is_pinned': True, 'category_id': None}, headers=headers).json
client.put
client.get('/api/v1/note', params={'uncategorized': True}, headers=headers).json
```

<a id="fn-d21ec54f2da87df0"></a>

## test_note_keyword_filter

源码：[L159](D:/Project/learnLittle/tests/test_notes_categories.py:159)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

创建两条不同主题笔记，列表 keyword 只命中 Redis 项。针对列表 SQL 过滤，不是向量检索效果评测。

**输入与签名**

```python
def test_note_keyword_filter(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert hit['total'] == 1 and hit['items'][0]['title'] == 'Redis 锁定机制'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_register_and_login
client.post
client.get('/api/v1/note', params={'keyword': 'redis'}, headers=headers).json
client.get
```

<a id="fn-d67713242f6e1310"></a>

## test_note_trash_restore_permanent

源码：[L168](D:/Project/learnLittle/tests/test_notes_categories.py:168)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

按创建、软删、回收站、恢复、再永久删除顺序检查各列表。验证生命周期状态，不代表直接永久删活跃项已被禁止。

**输入与签名**

```python
def test_note_trash_restore_permanent(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert client.get('/api/v1/note', headers=headers).json()['data']['total'] == 0
assert len(bin_items) == 1 and bin_items[0]['id'] == note_id
assert client.get('/api/v1/note', headers=headers).json()['data']['total'] == 1
assert client.get('/api/v1/note/recycle-bin', headers=headers).json()['data'] == []
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_register_and_login
client.post('/api/v1/note', json={'title': '待删笔记', 'content': 'x'}, headers=headers).json
client.post
client.delete
client.get('/api/v1/note', headers=headers).json
client.get
client.get('/api/v1/note/recycle-bin', headers=headers).json
len
```

<a id="fn-38e060d1aab57fa0"></a>

## test_category_delete_unties_notes

源码：[L190](D:/Project/learnLittle/tests/test_notes_categories.py:190)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

删有笔记的分类后读笔记，断言仍存在但 category_id=None。保护笔记不被分类删除连带移除。

**输入与签名**

```python
def test_category_delete_unties_notes(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert detail['category_id'] is None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_register_and_login
_find
_tree
client.post('/api/v1/note', json={'title': '挂载笔记', 'content': 'c', 'category_id': tech['id']}, headers=headers).json
client.post
client.delete
client.get(f'/api/v1/note/{note_id}', headers=headers).json
client.get
```

<a id="fn-cd5c5f0e99cb20f2"></a>

## test_cross_user_isolation

源码：[L206](D:/Project/learnLittle/tests/test_notes_categories.py:206)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

两用户分别登录，B 对 A 笔记读/改/删都 404，各用户默认分类 ID 不同。验证用户隔离且不泄露资源存在性。

**输入与签名**

```python
def test_cross_user_isolation(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert client.get(f'/api/v1/note/{note_id}', headers=headers_b).status_code == 404
assert client.put(f'/api/v1/note/{note_id}', json={'title': '偷改'}, headers=headers_b).status_code == 404
assert client.delete(f'/api/v1/note/{note_id}', headers=headers_b).status_code == 404
assert _find(b_tree, '技术')['id'] != tech_a['id']
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_register_and_login
_find
_tree
client.post('/api/v1/note', json={'title': '私密笔记', 'content': 'secret', 'category_id': tech_a['id']}, headers=headers_a).json
client.post
client.get
client.put
client.delete
```

<a id="fn-c34b6f88721d9cad"></a>

## test_pinned_note_sorts_first

源码：[L225](D:/Project/learnLittle/tests/test_notes_categories.py:225)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

创建早晚两笔记后置顶早项，断言列表第一是它。覆盖排序优先级。

**输入与签名**

```python
def test_pinned_note_sorts_first(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert items[0]['title'] == '早'
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_register_and_login
client.post('/api/v1/note', json={'title': '早', 'content': '1'}, headers=headers).json
client.post
client.put
client.get('/api/v1/note', headers=headers).json
client.get
```

<a id="fn-a7821ca859d7d7f1"></a>

## test_category_recycle_restore_ancestors

源码：[L237](D:/Project/learnLittle/tests/test_notes_categories.py:237)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

先删孩子后删父，再恢复孩子，检查祖先一起恢复。与先删父导致活跃孩子提升的场景不同。

**输入与签名**

```python
def test_category_recycle_restore_ancestors(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert work['id'] in ids and script['id'] in ids
assert restored.status_code == 200
assert restored.json()['data']['restored_count'] >= 2
assert _find(tree, '工作') is not None
assert _find(tree, '脚本') is not None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_register_and_login
_find
_tree
client.delete
client.get('/api/v1/category/recycle-bin', headers=headers).json
client.get
client.post
restored.json
```

<a id="fn-1d14b330d5f04952"></a>

## test_category_permanent_delete_and_cleanup

源码：[L257](D:/Project/learnLittle/tests/test_notes_categories.py:257)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

验证手动永久删分类，再把另一已删分类时间改旧并调用清理，确认消失。不是等待真实定时器触发。

**输入与签名**

```python
def test_category_permanent_delete_and_cleanup(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert wiped.status_code == 200
assert all((item['id'] != flash['id'] for item in bin_data['categories']))
assert asyncio.run(_age_and_clean()) >= 1
assert all((item['id'] != other['id'] for item in leftover['categories']))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_register_and_login
_find
_tree
client.delete
client.get('/api/v1/category/recycle-bin', headers=headers).json
client.get
all
asyncio.run
_age_and_clean
```

<a id="fn-af3a5e549e1de0a4"></a>

## test_category_permanent_delete_and_cleanup._age_and_clean

源码：[L274](D:/Project/learnLittle/tests/test_notes_categories.py:274)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

在测试库把 deleted_at 改为十五天前并 commit，再调十四天 cleanup 提交返回数量。制造可控过期条件。

**输入与签名**

```python
async def _age_and_clean()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return count
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
factory
(await db.execute(select(NoteCategory).where(NoteCategory.id == other['id']))).scalar_one
db.execute
select(NoteCategory).where
select
datetime.now
timedelta
db.commit
cleanup_expired_categories
```

<a id="fn-0545acad6423c329"></a>

## test_category_reorder_and_merge

源码：[L292](D:/Project/learnLittle/tests/test_notes_categories.py:292)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

反转完整顶级排序并检查响应，再合并阅读到学习，确认来源软删进入回收站。覆盖正常合并路径，不证明所有冲突分支。

**输入与签名**

```python
def test_category_reorder_and_merge(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert resp.status_code == 200
assert names == list(reversed(['工作', '学习', '技术', '生活', '闪念', '阅读', '三体', '其他']))
assert merged.status_code == 200
assert merged.json()['data']['merged_count'] == 1
assert _find(tree, '阅读') is None
assert _find(tree, '学习') is not None
assert reading['id'] in bin_ids
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_register_and_login
_tree
list
reversed
client.post
_find
merged.json
client.get('/api/v1/category/recycle-bin', headers=headers).json
client.get
```

<a id="fn-e86e08191072b6d7"></a>

## test_note_format_txt_and_move_category

源码：[L328](D:/Project/learnLittle/tests/test_notes_categories.py:328)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

验证 txt 创建/读取、更新不能改 format、移为未分类，非法 pdf 创建 422。区分 Schema 输入约束与业务移动。

**输入与签名**

```python
def test_note_format_txt_and_move_category(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert created.status_code == 200
assert created.json()['data']['format'] == 'txt'
assert detail['format'] == 'txt'
assert client.get(f'/api/v1/note/{note_id}', headers=headers).json()['data']['format'] == 'txt'
assert moved.status_code == 200
assert moved.json()['data']['category_id'] is None
assert client.post('/api/v1/note', json={'title': '坏类型', 'content': 'x', 'format': 'pdf'}, headers=headers).status_code == 422
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_register_and_login
_find
_tree
client.post
created.json
client.get(f'/api/v1/note/{note_id}', headers=headers).json
client.get
client.put
moved.json
```

<a id="fn-11a7c1cfce0e86a5"></a>

## test_note_batch_and_cleanup

源码：[L362](D:/Project/learnLittle/tests/test_notes_categories.py:362)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

批量置顶/移动/删除/恢复/永久删除检查逐项结果，再人为过期一条清理。验证批量服务主要成功路径。

**输入与签名**

```python
def test_note_batch_and_cleanup(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert pinned.status_code == 200
assert client.get(f'/api/v1/note/{id1}', headers=headers).json()['data']['is_pinned'] is True
assert moved.json()['data']['success_count'] == 2
assert client.get(f'/api/v1/note/{id1}', headers=headers).json()['data']['category_id'] == learning['id']
assert deleted.json()['data']['success_count'] == 2
assert {item['id'] for item in bin_items} >= {id2, id3}
assert all(('days_remaining' in item for item in bin_items))
assert restored.json()['data']['success_count'] == 1
```

另有 4 个出口/断言，完整条件见源码。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_register_and_login
_find
_tree
client.post('/api/v1/note', json={'title': 'A', 'content': '1'}, headers=headers).json
client.post
client.post('/api/v1/note', json={'title': 'B', 'content': '2'}, headers=headers).json
client.post('/api/v1/note', json={'title': 'C', 'content': '3'}, headers=headers).json
client.get(f'/api/v1/note/{id1}', headers=headers).json
client.get
moved.json
deleted.json
client.get('/api/v1/note/recycle-bin', headers=headers).json
all
restored.json
wiped.json
client.post('/api/v1/note', json={'title': '过期', 'content': 'x'}, headers=headers).json
client.delete
asyncio.run
_age_and_clean
```

<a id="fn-a79986431c5e59ca"></a>

## test_note_batch_and_cleanup._age_and_clean

源码：[L422](D:/Project/learnLittle/tests/test_notes_categories.py:422)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

把测试笔记 deleted_at 改旧，调用 cleanup_expired_notes 并提交。独立事务便于确认清理条件。

**输入与签名**

```python
async def _age_and_clean()
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return count
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
factory
(await db.execute(select(Note).where(Note.id == doomed))).scalar_one
db.execute
select(Note).where
select
datetime.now
timedelta
db.commit
cleanup_expired_notes
```

<a id="fn-b8912ea74cfafa79"></a>

## test_note_keyword_search_title_outranks_content

源码：[L440](D:/Project/learnLittle/tests/test_notes_categories.py:440)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

检查 LIKE 百分号字面匹配、标题比正文靠前及 1.0/0.5 展示分，排除已删和其他用户。SQLite 环境不证明 MySQL FULLTEXT 效果。

**输入与签名**

```python
def test_note_keyword_search_title_outranks_content(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert wild.status_code == 200
assert wild.json()['data']['results'] == []
assert resp.status_code == 200
assert title_id in ids and content_id in ids
assert deleted_id not in ids
assert ids.index(title_id) < ids.index(content_id)
assert scores[title_id] == 1.0
assert scores[content_id] == 0.5
```

另有 1 个出口/断言，完整条件见源码。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_register_and_login
client.post('/api/v1/note', json={'title': 'Redis 笔记', 'content': '随便写点'}, headers=headers).json
client.post
client.post('/api/v1/note', json={'title': '缓存策略', 'content': '用 Redis 做锁定'}, headers=headers).json
client.post('/api/v1/note', json={'title': 'Redis 回收', 'content': 'x'}, headers=headers).json
client.delete
wild.json
resp.json
ids.index
client.post('/api/v1/note/search', json={'query': 'Redis'}, headers=other).json
```

<a id="fn-34cd3f09374e5a7d"></a>

## test_note_template_crud_apply_and_isolation

源码：[L494](D:/Project/learnLittle/tests/test_notes_categories.py:494)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

创建/列表/改名/读取模板、套用得到笔记、跨用户禁止、删除后 404。验证模板到普通笔记创建链。

**输入与签名**

```python
def test_note_template_crud_apply_and_isolation(client: TestClient)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert created.status_code == 200
assert created.json()['data']['name'] == '会议纪要'
assert any((item['id'] == tid for item in listed))
assert detail['name'] == '周会纪要'
assert applied.status_code == 200
assert note['title'] == '周会纪要'
assert '## 议题' in note['content']
assert client.get(f'/api/v1/note-template/{tid}', headers=stranger).status_code == 404
```

另有 3 个出口/断言，完整条件见源码。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_register_and_login
client.post
created.json
client.get('/api/v1/note-template', headers=headers).json
client.get
any
client.put
client.get(f'/api/v1/note-template/{tid}', headers=headers).json
applied.json
client.get(f'/api/v1/note/{note_id}', headers=headers).json
client.delete
```

<a id="fn-4548c023d536ceac"></a>

## test_note_ai_assist_uses_injected_fn

源码：[L541](D:/Project/learnLittle/tests/test_notes_categories.py:541)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

注入按提示返回结果的假模型，验证补全、扩写、标签接口及非法模式 422。不测试真实供应商输出质量。

**输入与签名**

```python
def test_note_ai_assist_uses_injected_fn(client: TestClient, monkeypatch)
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
assert auto.status_code == 200
assert '测试用例' in auto.json()['data']['completion']
assert write.json()['data']['result'] == '扩写后的段落。'
assert tags.json()['data']['tags'] == ['fastapi', '测试', 'pytest']
assert empty.status_code == 422
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
monkeypatch.setattr
note_ai_service.set_note_ai_fn
_register_and_login
client.post
auto.json
write.json
tags.json
```

<a id="fn-ed3639e7b14ca328"></a>

## test_note_ai_assist_uses_injected_fn.fake_complete

源码：[L544](D:/Project/learnLittle/tests/test_notes_categories.py:544)；任务：[第 10 章](D:/Project/learnLittle/docs/backend-tutorial/10-tests.md)。

按 prompt 中补全/标签/扩写关键词返回固定文字，其他返回续写。用于观察每个入口是否构造了正确任务提示。

**输入与签名**

```python
async def fake_complete(prompt: str) -> str
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return '接下来写测试用例。'
return 'fastapi, 测试, pytest'
return '扩写后的段落。'
return '续写后的段落。'
```
