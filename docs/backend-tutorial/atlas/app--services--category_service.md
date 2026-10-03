# app/services/category_service.py

[源码](D:/Project/learnLittle/app/services/category_service.py) | [任务流程 03](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

最多三层树与软删/恢复/合并规则；树算法一次加载再计算。

## 本文件导航

- [seed_template_tree](#fn-674267313d6b72ca)
- [seed_template_tree._seed](#fn-cd089a549c944458)
- [_not_found](#fn-b205866b989521fc)
- [_load_active](#fn-92a4538fd0f099f7)
- [_depth_of](#fn-8ed2219d89b61ac3)
- [_subtree_height](#fn-38d46210fcf789a5)
- [_is_descendant](#fn-e7e3b602922d4fcc)
- [_assert_same_name_free](#fn-a9c897aa090b2b95)
- [_next_sort_order](#fn-8c3b4d712550dd26)
- [_to_dict](#fn-8a3d32893ee40e4e)
- [get_category_tree](#fn-eea3605e85e3f381)
- [get_category_tree.build](#fn-614a036d347996ab)
- [get_category_tree.build.<lambda@172:60>](#fn-518086f50d071ed7)
- [get_category_dict](#fn-f66069ddc9bb7703)
- [create_category](#fn-ce5d4d5d473a7ef3)
- [update_category](#fn-a2ec3476906ef6d2)
- [move_category](#fn-960c5ea2a205b02f)
- [_load_deleted](#fn-b8407dcece6f6d1c)
- [_promote_active_children](#fn-56be8f4057ba3478)
- [soft_delete_category](#fn-b748670b312cafdf)
- [restore_category](#fn-e36307612382ad0a)
- [restore_category.collect_deleted_children](#fn-a10360a4f08b25dd)
- [permanent_delete_category](#fn-fe3c28ef778d34bd)
- [list_recycle_bin](#fn-1ee01afdc07f1d41)
- [list_recycle_bin.count_descendants](#fn-e1b801a4f564cfed)
- [reorder_categories](#fn-7235fe0eb0eacde4)
- [merge_categories](#fn-66335f5de4bca695)
- [merge_categories.<lambda@507:19>](#fn-16aed68485505a86)
- [cleanup_expired_categories](#fn-519436530b2f047e)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
MAX_DEPTH = 3

TEMPLATE_TREE: list[dict] = [{'name': '工作', 'children': [{'name': '脚本'}, {'name': '项目文档', 'children': [{'name': 'XXX服务_V1.0.06'}]}]}, {'name': '学习'}, {'name': '技术', 'children': [{'name': 'Flutter'}, {'name': 'Java'}, {'name': 'Nodejs'}, {'name': 'Vue'}]}, {'name': '生活', 'children': [{'name': '手工'}, {'name': '旅游'}, {'name': '育儿'}, {'name': '菜谱'}]}, {'name': '闪念'}, {'name': '阅读'}, {'name': '三体'}, {'name': '其他'}]
```

<a id="fn-674267313d6b72ca"></a>

## seed_template_tree

源码：[L48](D:/Project/learnLittle/app/services/category_service.py:48)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

遍历默认分类模板，为新用户递归创建分类。与 User 使用同一 SQL session，注册失败时一起回滚。

**输入与签名**

```python
async def seed_template_tree(db: AsyncSession, user_id: str) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_seed
```

<a id="fn-cd089a549c944458"></a>

## seed_template_tree._seed

源码：[L51](D:/Project/learnLittle/app/services/category_service.py:51)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

递归处理一个模板节点，生成 ID、写 parent_id/排序等，再处理孩子。是播种细节，不负责单独 commit。

**输入与签名**

```python
async def _seed(nodes: list[dict], parent_id: str | None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
enumerate
NoteCategory
str
uuid.uuid4
db.add
node.get
_seed
```

<a id="fn-b205866b989521fc"></a>

## _not_found

源码：[L69](D:/Project/learnLittle/app/services/category_service.py:69)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

构造分类不存在的统一业务异常。用于隐藏无权访问与不存在之间的差异。

**输入与签名**

```python
def _not_found() -> BusinessError
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return BusinessError(code=ErrorCode.CATEGORY_NOT_FOUND, http_status=404)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
BusinessError
```

<a id="fn-92a4538fd0f099f7"></a>

## _load_active

源码：[L73](D:/Project/learnLittle/app/services/category_service.py:73)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

一次读取当前用户全部未删除分类并形成按 ID 索引，供树计算。避免深度检查每走一层都发 SQL。

**输入与签名**

```python
async def _load_active(db: AsyncSession, user_id: str) -> dict[str, NoteCategory]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {cat.id: cat for cat in result.scalars()}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
db.execute
select(NoteCategory).where
select
NoteCategory.deleted_at.is_
result.scalars
```

<a id="fn-8ed2219d89b61ac3"></a>

## _depth_of

源码：[L83](D:/Project/learnLittle/app/services/category_service.py:83)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

沿父链计算节点深度，根为一层。创建/移动用它结合子树高度判断三层限制。

**输入与签名**

```python
def _depth_of(category_id: str, cats: dict[str, NoteCategory]) -> int
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return depth
```

<a id="fn-38d46210fcf789a5"></a>

## _subtree_height

源码：[L93](D:/Project/learnLittle/app/services/category_service.py:93)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

递归计算指定节点向下的最大层数，单节点为一。移动限制考虑整棵子树，而不只考虑根节点。

**输入与签名**

```python
def _subtree_height(category_id: str, cats: dict[str, NoteCategory]) -> int
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return 1
return 1 + max((_subtree_height(child, cats) for child in children))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
cats.values
max
_subtree_height
```

<a id="fn-e7e3b602922d4fcc"></a>

## _is_descendant

源码：[L101](D:/Project/learnLittle/app/services/category_service.py:101)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

从节点沿祖先关系判断是否位于目标祖先之下。用于阻止移动成环和非法合并。

**输入与签名**

```python
def _is_descendant(candidate_id: str, ancestor_id: str, cats: dict[str, NoteCategory]) -> bool
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return True
return False
```

<a id="fn-a9c897aa090b2b95"></a>

## _assert_same_name_free

源码：[L110](D:/Project/learnLittle/app/services/category_service.py:110)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

检查同用户、同父级活跃分类中是否已有名称，可排除自己。是应用级唯一性检查，非数据库唯一约束替代品。

**输入与签名**

```python
async def _assert_same_name_free(db: AsyncSession, user_id: str, parent_id: str | None, name: str, exclude_id: str | None=None) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
select(NoteCategory).where
select
NoteCategory.deleted_at.is_
NoteCategory.parent_id.is_
stmt.where
(await db.execute(stmt)).scalar_one_or_none
db.execute
BusinessError
```

<a id="fn-8c3b4d712550dd26"></a>

## _next_sort_order

源码：[L126](D:/Project/learnLittle/app/services/category_service.py:126)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

读取同级最大排序号并加一，给新节点找位置。当前 max=0 会被 or -1 当作空，排序边界见第 11 章。

**输入与签名**

```python
async def _next_sort_order(db: AsyncSession, user_id: str, parent_id: str | None) -> int
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return ((await db.execute(stmt)).scalar_one() or -1) + 1
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
select(func.max(NoteCategory.sort_order)).where
select
func.max
NoteCategory.deleted_at.is_
NoteCategory.parent_id.is_
(await db.execute(stmt)).scalar_one
db.execute
```

<a id="fn-8a3d32893ee40e4e"></a>

## _to_dict

源码：[L135](D:/Project/learnLittle/app/services/category_service.py:135)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

把分类实体、直属笔记数和孩子转换为树节点字典。主要是响应数据塑形，不修改实体。

**输入与签名**

```python
def _to_dict(cat: NoteCategory, note_count: int, children: list[dict]) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'id': cat.id, 'name': cat.name, 'parent_id': cat.parent_id, 'icon': cat.icon, 'color': cat.color, 'sort_order': cat.sort_order, 'note_count': note_count, 'created_at': cat.created_at, 'updated_at': cat.updated_at, 'children': chi ... [截短，完整见源码]
```

<a id="fn-eea3605e85e3f381"></a>

## get_category_tree

源码：[L152](D:/Project/learnLittle/app/services/category_service.py:152)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

加载活跃分类、统计每类直属活跃笔记数，再按父级递归构建有序树。返回树列表，不把后代笔记数混成直属数。

**输入与签名**

```python
async def get_category_tree(db: AsyncSession, user_id: str) -> list[dict]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return build(None)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_load_active
select(Note.category_id, func.count(Note.id)).where(Note.user_id == user_id, Note.deleted_at.is_(None), Note.category_id.isnot(None)).group_by
select(Note.category_id, func.count(Note.id)).where
select
func.count
Note.deleted_at.is_
Note.category_id.isnot
(await db.execute(count_stmt)).all
db.execute
cats.values
children_map.setdefault(cat.parent_id, []).append
children_map.setdefault
build
```

<a id="fn-614a036d347996ab"></a>

## get_category_tree.build

源码：[L171](D:/Project/learnLittle/app/services/category_service.py:171)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

从 parent_id 对应节点组排序，递归把每个孩子填入 children。服务于树响应，不额外产生数据库事务。

**输入与签名**

```python
def build(parent_id: str | None) -> list[dict]
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return [_to_dict(cat, note_counts.get(cat.id, 0), build(cat.id)) for cat in nodes]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
sorted
children_map.get
_to_dict
note_counts.get
build
```

<a id="fn-518086f50d071ed7"></a>

## get_category_tree.build.<lambda@172:60>

源码：[L172](D:/Project/learnLittle/app/services/category_service.py:172)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

树响应构造中以 sort_order 升序排列同级节点。相同 sort_order 没有在此额外定义唯一性。

**输入与签名**

```python
lambda c: c.sort_order
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
表达式返回 c.sort_order
```

<a id="fn-f66069ddc9bb7703"></a>

## get_category_dict

源码：[L180](D:/Project/learnLittle/app/services/category_service.py:180)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

读取单个当前用户活跃分类并计算直属笔记数，供写操作后回显。其 children 表现不等于重新查询整个树。

**输入与签名**

```python
async def get_category_dict(db: AsyncSession, user_id: str, category_id: str) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return _to_dict(cat, note_count, children=[])
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_load_active
cats.get
_not_found
select(func.count(Note.id)).where
select
func.count
Note.deleted_at.is_
(await db.execute(count_stmt)).scalar_one
db.execute
_to_dict
```

<a id="fn-ce5d4d5d473a7ef3"></a>

## create_category

源码：[L196](D:/Project/learnLittle/app/services/category_service.py:196)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

校验父分类、同级名称和三层限制，设置排序并写实体。返回 ORM 对象，外层事务统一提交。

**输入与签名**

```python
async def create_category(db: AsyncSession, user_id: str, data: CategoryCreate) -> NoteCategory
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return cat
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_load_active
cats.get
_not_found
_depth_of
BusinessError
_assert_same_name_free
NoteCategory
str
uuid.uuid4
_next_sort_order
db.add
db.flush
```

<a id="fn-a2ec3476906ef6d2"></a>

## update_category

源码：[L226](D:/Project/learnLittle/app/services/category_service.py:226)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

更新分类名称/颜色/图标等，名称改变时检查同级冲突。不会借重命名自动移动子树。

**输入与签名**

```python
async def update_category(db: AsyncSession, user_id: str, category_id: str, data: CategoryUpdate) -> NoteCategory
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return cat
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_load_active
cats.get
_not_found
_assert_same_name_free
db.flush
```

<a id="fn-960c5ea2a205b02f"></a>

## move_category

源码：[L243](D:/Project/learnLittle/app/services/category_service.py:243)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

验证新父节点归属、拒绝自己/后代环，检查移动后子树高度和同名冲突，再更新父级与排序。整棵子树关系由 parent_id 链继承。

**输入与签名**

```python
async def move_category(db: AsyncSession, user_id: str, category_id: str, new_parent_id: str | None) -> NoteCategory
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return cat
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_load_active
cats.get
_not_found
BusinessError
_is_descendant
_depth_of
_subtree_height
_assert_same_name_free
_next_sort_order
db.flush
```

<a id="fn-b8407dcece6f6d1c"></a>

## _load_deleted

源码：[L279](D:/Project/learnLittle/app/services/category_service.py:279)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

读取当前用户回收站中的分类集合，供恢复与数量计算。与 _load_active 的选择条件相反。

**输入与签名**

```python
async def _load_deleted(db: AsyncSession, user_id: str, category_id: str) -> NoteCategory
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return cat
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(await db.execute(select(NoteCategory).where(NoteCategory.id == category_id, NoteCategory.user_id == user_id, NoteCategory.deleted_at.isnot(None)))).scalar_one_or_none
db.execute
select(NoteCategory).where
select
NoteCategory.deleted_at.isnot
_not_found
```

<a id="fn-56be8f4057ba3478"></a>

## _promote_active_children

源码：[L294](D:/Project/learnLittle/app/services/category_service.py:294)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

物理删父分类前把仍活跃的直接孩子升为顶级，避免数据库 CASCADE 把它们一起删掉。不会恢复其他已删除孩子。

**输入与签名**

```python
async def _promote_active_children(db: AsyncSession, cat: NoteCategory) -> None
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return None
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
(await db.execute(select(NoteCategory).where(NoteCategory.parent_id == cat.id, NoteCategory.user_id == cat.user_id, NoteCategory.deleted_at.is_(None)))).scalars().all
(await db.execute(select(NoteCategory).where(NoteCategory.parent_id == cat.id, NoteCategory.user_id == cat.user_id, NoteCategory.deleted_at.is_(None)))).scalars
db.execute
select(NoteCategory).where
select
NoteCategory.deleted_at.is_
_next_sort_order
enumerate
db.flush
```

<a id="fn-b748670b312cafdf"></a>

## soft_delete_category

源码：[L314](D:/Project/learnLittle/app/services/category_service.py:314)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

将活跃孩子提升到被删分类的父级，把直属笔记设为未分类，再标 deleted_at。返回影响数量，不是递归删除整树。

**输入与签名**

```python
async def soft_delete_category(db: AsyncSession, user_id: str, category_id: str) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'subcategory_count': promoted, 'note_count': note_count}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_load_active
cats.get
_not_found
datetime.now
cats.values
(await db.execute(select(func.count(Note.id)).where(Note.category_id == category_id, Note.user_id == user_id, Note.deleted_at.is_(None)))).scalar_one
db.execute
select(func.count(Note.id)).where
select
func.count
Note.deleted_at.is_
Note.__table__.update().where(Note.category_id == category_id, Note.user_id == user_id).values
Note.__table__.update().where
Note.__table__.update
db.flush
```

<a id="fn-e36307612382ad0a"></a>

## restore_category

源码：[L347](D:/Project/learnLittle/app/services/category_service.py:347)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

恢复当前用户目标分类，同时补回已删除祖先链并收集可恢复已删后代。已经提升的活跃孩子和解绑笔记不重新挂回。

**输入与签名**

```python
async def restore_category(db: AsyncSession, user_id: str, category_id: str) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'restored_count': len(unique)}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_load_deleted
(await db.execute(select(NoteCategory).where(NoteCategory.id == current_id, NoteCategory.user_id == user_id))).scalar_one_or_none
db.execute
select(NoteCategory).where
select
to_restore.append
(await db.execute(select(NoteCategory).where(NoteCategory.user_id == user_id))).scalars().all
(await db.execute(select(NoteCategory).where(NoteCategory.user_id == user_id))).scalars
defaultdict
children_map[item.parent_id].append
collect_deleted_children
set
seen.add
unique.append
_assert_same_name_free
db.flush
len
```

<a id="fn-a10360a4f08b25dd"></a>

## restore_category.collect_deleted_children

源码：[L374](D:/Project/learnLittle/app/services/category_service.py:374)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

在已删节点集合中递归收集目标的后代，供一次恢复处理。不会凭空推断删除前已改变的活跃树关系。

**输入与签名**

```python
def collect_deleted_children(node: NoteCategory) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
children_map.get
to_restore.append
collect_deleted_children
```

<a id="fn-fe3c28ef778d34bd"></a>

## permanent_delete_category

源码：[L397](D:/Project/learnLittle/app/services/category_service.py:397)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

要求目标为本用户已删分类，先保护活跃孩子再物理删除。关联已删后代可被 FK 级联删除，操作不可用普通恢复撤销。

**输入与签名**

```python
async def permanent_delete_category(db: AsyncSession, user_id: str, category_id: str) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'deleted_name': name}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_load_deleted
_promote_active_children
db.delete
db.flush
```

<a id="fn-1ee01afdc07f1d41"></a>

## list_recycle_bin

源码：[L406](D:/Project/learnLittle/app/services/category_service.py:406)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

返回软删分类及后代数量、剩余保留时间等展示信息。统计不是执行恢复或清理。

**输入与签名**

```python
async def list_recycle_bin(db: AsyncSession, user_id: str) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'categories': items, 'total': len(items)}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
list
(await db.execute(select(NoteCategory).where(NoteCategory.user_id == user_id, NoteCategory.deleted_at.isnot(None)).order_by(NoteCategory.deleted_at.desc()))).scalars().all
(await db.execute(select(NoteCategory).where(NoteCategory.user_id == user_id, NoteCategory.deleted_at.isnot(None)).order_by(NoteCategory.deleted_at.desc()))).scalars
db.execute
select(NoteCategory).where(NoteCategory.user_id == user_id, NoteCategory.deleted_at.isnot(None)).order_by
select(NoteCategory).where
select
NoteCategory.deleted_at.isnot
NoteCategory.deleted_at.desc
defaultdict
children_map[cat.parent_id].append
get_settings
datetime.now
items.append
max
count_descendants
len
```

<a id="fn-e1b801a4f564cfed"></a>

## list_recycle_bin.count_descendants

源码：[L420](D:/Project/learnLittle/app/services/category_service.py:420)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

在已删除关系中递归计算某回收站节点的后代数。是展示计数辅助函数，不操作数据库状态。

**输入与签名**

```python
def count_descendants(node: NoteCategory) -> int
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return len(kids) + sum((count_descendants(child) for child in kids))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
children_map.get
len
sum
count_descendants
```

<a id="fn-7235fe0eb0eacde4"></a>

## reorder_categories

源码：[L444](D:/Project/learnLittle/app/services/category_service.py:444)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

确认给定排序 ID 集合对应指定父级的分类，按位置更新 sort_order。当前 set 比较不能替代显式重复 ID 检查。

**输入与签名**

```python
async def reorder_categories(db: AsyncSession, user_id: str, data: CategoryReorderRequest) -> None
```

**出口与观察点**

没有直接 return/yield/assert；通常通过修改状态、调用其他函数或抛异常产生结果，正常走到末尾返回 None。请结合上面的职责说明辨认具体副作用。

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
_load_active
_not_found
cats.values
set
BusinessError
enumerate
db.flush
```

<a id="fn-66335f5de4bca695"></a>

## merge_categories

源码：[L462](D:/Project/learnLittle/app/services/category_service.py:462)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

检查来源/目标关系、深度等条件，迁移笔记与孩子到目标并软删来源。写同一 SQL 事务，但不是保留完整历史的可逆合并。

**输入与签名**

```python
async def merge_categories(db: AsyncSession, user_id: str, source_ids: list[str], target_id: str) -> dict
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return {'merged_count': len(sources), 'target_id': target_id}
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
list
dict.fromkeys
_load_active
cats.get
_not_found
BusinessError
_is_descendant
sources.append
_depth_of
_subtree_height
cats.values
_assert_same_name_free
db.execute
update(Note).where(Note.user_id == user_id, Note.category_id.in_(source_ids)).values
update(Note).where
update
Note.category_id.in_
_next_sort_order
set
moved.sort
enumerate
datetime.now
db.flush
len
```

<a id="fn-16aed68485505a86"></a>

## merge_categories.<lambda@507:19>

源码：[L507](D:/Project/learnLittle/app/services/category_service.py:507)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

合并分类时以 sort_order 排列要处理的项，保留已有排序意图。业务关系检查在外层 merge。

**输入与签名**

```python
lambda item: item.sort_order
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
表达式返回 item.sort_order
```

<a id="fn-519436530b2f047e"></a>

## cleanup_expired_categories

源码：[L519](D:/Project/learnLittle/app/services/category_service.py:519)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

筛选超保留期回收站分类，保护活跃孩子并删除，返回处理数量。由调度包装器提交，不按活跃分类年龄删除。

**输入与签名**

```python
async def cleanup_expired_categories(db: AsyncSession, days: int | None=None) -> int
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return len(expired)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
datetime.now
timedelta
get_settings
list
(await db.execute(select(NoteCategory).where(NoteCategory.deleted_at.isnot(None), NoteCategory.deleted_at <= cutoff))).scalars().all
(await db.execute(select(NoteCategory).where(NoteCategory.deleted_at.isnot(None), NoteCategory.deleted_at <= cutoff))).scalars
db.execute
select(NoteCategory).where
select
NoteCategory.deleted_at.isnot
_promote_active_children
db.delete
db.flush
len
```
