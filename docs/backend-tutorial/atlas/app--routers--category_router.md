# app/routers/category_router.py

[源码](D:/Project/learnLittle/app/routers/category_router.py) | [任务流程 03](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md) | [详解目录](D:/Project/learnLittle/docs/backend-tutorial/atlas/README.md)

分类树、移动、回收站、排序和批量合并 HTTP 入口。

## 本文件导航

- [category_tree](#fn-6509b3f75757abeb)
- [create_category](#fn-5c7141df0d68a32f)
- [update_category](#fn-a08d8f0c95435cb0)
- [move_category](#fn-b5a99718b72087d0)
- [delete_category](#fn-0b4d4cb3395b8f24)
- [recycle_bin](#fn-a3a6aa0e4408f89d)
- [restore_category](#fn-65855ef5a65a9443)
- [permanent_delete_category](#fn-b1402f4647a5c320)
- [reorder_categories](#fn-b26b68305f50e4c2)
- [batch_operation](#fn-6d0a4319b5ab93ae)

## 模块声明

常量、类型别名、注入槽及模块级实例如下；赋值不等于业务请求已经执行。

```python
router = APIRouter()
```

<a id="fn-6509b3f75757abeb"></a>

## category_tree

源码：[L35](D:/Project/learnLittle/app/routers/category_router.py:35)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

返回当前用户活跃分类树与直属笔记数。权限来自 Depends，树构建在 service。

**输入与签名**

```python
async def category_tree(user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.get('/category/tree', summary='获取分类树')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=await category_service.get_category_tree(db, user_id))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
success_response
category_service.get_category_tree
router.get
```

<a id="fn-5c7141df0d68a32f"></a>

## create_category

源码：[L43](D:/Project/learnLittle/app/routers/category_router.py:43)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

接创建数据，service 创建后再查 get_category_dict 回显计数等字段。不是只返回未经验证的请求体。

**输入与签名**

```python
async def create_category(data: CategoryCreate, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.post('/category', summary='创建分类')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=detail)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
category_service.create_category
category_service.get_category_dict
success_response
router.post
```

<a id="fn-a08d8f0c95435cb0"></a>

## update_category

源码：[L54](D:/Project/learnLittle/app/routers/category_router.py:54)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

委托修改名称/样式，再读规范分类响应。数据库事务由请求依赖统一提交。

**输入与签名**

```python
async def update_category(category_id: str, data: CategoryUpdate, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.put('/category/{category_id}', summary='更新分类')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=detail)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
category_service.update_category
category_service.get_category_dict
success_response
router.put
```

<a id="fn-b5a99718b72087d0"></a>

## move_category

源码：[L66](D:/Project/learnLittle/app/routers/category_router.py:66)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

把新 parent_id 交 service 检查环/深度并移动，再回显。路由本身不跳过服务层树规则。

**输入与签名**

```python
async def move_category(category_id: str, data: CategoryMoveRequest, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.post('/category/{category_id}/move', summary='移动分类')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=detail)
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
category_service.move_category
category_service.get_category_dict
success_response
router.post
```

<a id="fn-0b4d4cb3395b8f24"></a>

## delete_category

源码：[L78](D:/Project/learnLittle/app/routers/category_router.py:78)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

委托软删并返回子分类/笔记影响数量。删除会提升孩子、解绑笔记，不是递归全删。

**输入与签名**

```python
async def delete_category(category_id: str, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.delete('/category/{category_id}', summary='删除分类')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=impact, message='分类已删除')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
category_service.soft_delete_category
success_response
router.delete
```

<a id="fn-a3a6aa0e4408f89d"></a>

## recycle_bin

源码：[L88](D:/Project/learnLittle/app/routers/category_router.py:88)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

返回当前用户分类回收站展示数据。不会自动恢复祖先或删除子树。

**输入与签名**

```python
async def recycle_bin(user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.get('/category/recycle-bin', summary='回收站分类列表')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=await category_service.list_recycle_bin(db, user_id))
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
success_response
category_service.list_recycle_bin
router.get
```

<a id="fn-65855ef5a65a9443"></a>

## restore_category

源码：[L96](D:/Project/learnLittle/app/routers/category_router.py:96)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

委托恢复分类及需要的已删祖先/后代，包装恢复结果。不是重建删除前所有笔记挂载。

**输入与签名**

```python
async def restore_category(category_id: str, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.post('/category/{category_id}/restore', summary='恢复分类')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=result, message='分类已恢复')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
category_service.restore_category
success_response
router.post
```

<a id="fn-b1402f4647a5c320"></a>

## permanent_delete_category

源码：[L106](D:/Project/learnLittle/app/routers/category_router.py:106)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

委托已删分类物理删除并返回影响结果。活跃孩子保护在 service，操作不可逆。

**输入与签名**

```python
async def permanent_delete_category(category_id: str, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.delete('/category/{category_id}/permanent', summary='彻底删除分类')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data=result, message='分类已彻底删除')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
category_service.permanent_delete_category
success_response
router.delete
```

<a id="fn-b26b68305f50e4c2"></a>

## reorder_categories

源码：[L116](D:/Project/learnLittle/app/routers/category_router.py:116)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

接同级排序数据，交 service 验证并更新位置。一次请求完成同一组的 SQL 变更。

**输入与签名**

```python
async def reorder_categories(data: CategoryReorderRequest, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.post('/category/reorder', summary='批量重排分类')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(message='排序已更新')
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
category_service.reorder_categories
success_response
router.post
```

<a id="fn-6d0a4319b5ab93ae"></a>

## batch_operation

源码：[L126](D:/Project/learnLittle/app/routers/category_router.py:126)；任务：[第 03 章](D:/Project/learnLittle/docs/backend-tutorial/03-notes.md)。

delete 分支逐个删、merge 分支统一合并；restore/permanent 分支逐条捕获 BusinessError 收集结果。不同分支容错不同，不能概括成所有批量项都失败隔离。

**输入与签名**

```python
async def batch_operation(data: CategoryBatchRequest, user_id: str=Depends(get_current_user_id), db: AsyncSession=Depends(get_db_session))
```

装饰器/挂载：

```python
@router.post('/category/batch', summary='批量操作分类')
```

**出口与观察点**

下列是本函数直接作用域的 return/yield/assert 表达式；分支并非都会执行，嵌套函数的出口列在其自身条目。

```python
return success_response(data={'operation': 'delete', 'total': len(data.category_ids), 'subcategory_count': total_subs, 'note_count': total_notes}, message=f'批量删除完成：{len(data.category_ids)} 个分类')
return success_response(data={'operation': 'merge', **result}, message=f'合并完成：{result['merged_count']} 个分类已并入目标')
return success_response(data={'operation': data.operation, 'total': len(data.category_ids), 'success_count': len(success_ids), 'error_count': len(errors), 'errors': errors or None}, message=f'批量{action}完成：成功 {len(success_ids)} 个，失败 {len( ... [截短，完整见源码]
```

**调用线索**

下面是静态调用表达式，不是已解析的运行时调用图；同名、别名、注入和闭包需结合导入与上下文判断。

```text
Depends
category_service.soft_delete_category
success_response
len
BusinessError
category_service.merge_categories
category_service.permanent_delete_category
category_service.restore_category
success_ids.append
errors.append
router.post
```
