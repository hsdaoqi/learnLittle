"""分类服务：树形结构规则与生命周期。

规则（与原项目设计方案一致）：
- 树最多 3 级（根 = 第 1 级）
- 同一父分类下，活跃分类不允许同名（软删除记录不参与比较）
- 移动/建子分类前做环检测与深度校验
- 软删除分类时：活跃子分类提升到被删分类的父级，直属笔记变为「未分类」
- 恢复时级联拉回已删除的祖先，避免树断链；14 天后物理删除

所有函数都通过 user_id 强制用户隔离，跨用户访问一律视为不存在。
"""

import uuid
from collections import defaultdict
from datetime import datetime, timedelta

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.failed_response import BusinessError, ErrorCode
from app.models.category import NoteCategory
from app.models.note import Note
from app.config import get_settings
from app.schemas.category import CategoryCreate, CategoryReorderRequest, CategoryUpdate

MAX_DEPTH = 3

# 新用户注册时的默认分类树（节点名互不重复，最多 3 级）
TEMPLATE_TREE: list[dict] = [
    {"name": "工作", "children": [
        {"name": "脚本"},
        {"name": "项目文档", "children": [{"name": "XXX服务_V1.0.06"}]},
    ]},
    {"name": "学习"},
    {"name": "技术", "children": [
        {"name": "Flutter"}, {"name": "Java"}, {"name": "Nodejs"}, {"name": "Vue"},
    ]},
    {"name": "生活", "children": [
        {"name": "手工"}, {"name": "旅游"}, {"name": "育儿"}, {"name": "菜谱"},
    ]},
    {"name": "闪念"},
    {"name": "阅读"},
    {"name": "三体"},
    {"name": "其他"},
]


async def seed_template_tree(db: AsyncSession, user_id: str) -> None:
    """为新用户播种默认分类树（注册时调用，随注册同一事务提交）。"""

    async def _seed(nodes: list[dict], parent_id: str | None) -> None:
        for i, node in enumerate(nodes):
            cat = NoteCategory(
                id=str(uuid.uuid4()),
                user_id=user_id,
                parent_id=parent_id,
                name=node["name"],
                sort_order=i,
            )
            db.add(cat)
            if node.get("children"):
                await _seed(node["children"], cat.id)

    await _seed(TEMPLATE_TREE, None)


# ========== 内部工具 ==========

def _not_found() -> BusinessError:
    return BusinessError(code=ErrorCode.CATEGORY_NOT_FOUND, http_status=404)


async def _load_active(db: AsyncSession, user_id: str) -> dict[str, NoteCategory]:
    """加载该用户全部活跃分类（数量少，一次性载入内存做树运算）。"""
    result = await db.execute(
        select(NoteCategory).where(
            NoteCategory.user_id == user_id, NoteCategory.deleted_at.is_(None)
        )
    )
    return {cat.id: cat for cat in result.scalars()}


def _depth_of(category_id: str, cats: dict[str, NoteCategory]) -> int:
    """节点深度：根 = 1。"""
    depth = 0
    current: str | None = category_id
    while current:
        depth += 1
        current = cats[current].parent_id
    return depth


def _subtree_height(category_id: str, cats: dict[str, NoteCategory]) -> int:
    """以该节点为根的子树高度（只有自己 = 1）。"""
    children = [c.id for c in cats.values() if c.parent_id == category_id]
    if not children:
        return 1
    return 1 + max(_subtree_height(child, cats) for child in children)


def _is_descendant(candidate_id: str, ancestor_id: str, cats: dict[str, NoteCategory]) -> bool:
    current = cats[candidate_id].parent_id
    while current:
        if current == ancestor_id:
            return True
        current = cats[current].parent_id
    return False


async def _assert_same_name_free(
    db: AsyncSession, user_id: str, parent_id: str | None, name: str, exclude_id: str | None = None
) -> None:
    """同一父分类下的活跃分类中不允许同名。"""
    stmt = select(NoteCategory).where(
        NoteCategory.user_id == user_id,
        NoteCategory.deleted_at.is_(None),
        NoteCategory.parent_id.is_(parent_id) if parent_id is None else NoteCategory.parent_id == parent_id,
        NoteCategory.name == name,
    )
    if exclude_id:
        stmt = stmt.where(NoteCategory.id != exclude_id)
    if (await db.execute(stmt)).scalar_one_or_none():
        raise BusinessError(code=ErrorCode.CATEGORY_NAME_EXISTS, http_status=409)


async def _next_sort_order(db: AsyncSession, user_id: str, parent_id: str | None) -> int:
    stmt = select(func.max(NoteCategory.sort_order)).where(
        NoteCategory.user_id == user_id,
        NoteCategory.deleted_at.is_(None),
        NoteCategory.parent_id.is_(parent_id) if parent_id is None else NoteCategory.parent_id == parent_id,
    )
    return ((await db.execute(stmt)).scalar_one() or -1) + 1


def _to_dict(cat: NoteCategory, note_count: int, children: list[dict]) -> dict:
    return {
        "id": cat.id,
        "name": cat.name,
        "parent_id": cat.parent_id,
        "icon": cat.icon,
        "color": cat.color,
        "sort_order": cat.sort_order,
        "note_count": note_count,
        "created_at": cat.created_at,
        "updated_at": cat.updated_at,
        "children": children,
    }


# ========== 对外接口 ==========

async def get_category_tree(db: AsyncSession, user_id: str) -> list[dict]:
    """返回活跃分类树（含每类直属活跃笔记数），按 sort_order 排序。"""
    cats = await _load_active(db, user_id)

    count_stmt = (
        select(Note.category_id, func.count(Note.id))
        .where(
            Note.user_id == user_id,
            Note.deleted_at.is_(None),
            Note.category_id.isnot(None),
        )
        .group_by(Note.category_id)
    )
    note_counts = {cid: count for cid, count in (await db.execute(count_stmt)).all()}

    children_map: dict[str | None, list[NoteCategory]] = {}
    for cat in cats.values():
        children_map.setdefault(cat.parent_id, []).append(cat)

    def build(parent_id: str | None) -> list[dict]:
        nodes = sorted(children_map.get(parent_id, []), key=lambda c: c.sort_order)
        return [
            _to_dict(cat, note_counts.get(cat.id, 0), build(cat.id)) for cat in nodes
        ]

    return build(None)


async def get_category_dict(db: AsyncSession, user_id: str, category_id: str) -> dict:
    """获取单个活跃分类（含直属活跃笔记数），供创建/更新/移动后回显。"""
    cats = await _load_active(db, user_id)
    cat = cats.get(category_id)
    if cat is None:
        raise _not_found()

    count_stmt = select(func.count(Note.id)).where(
        Note.user_id == user_id,
        Note.deleted_at.is_(None),
        Note.category_id == category_id,
    )
    note_count = (await db.execute(count_stmt)).scalar_one()
    return _to_dict(cat, note_count, children=[])


async def create_category(db: AsyncSession, user_id: str, data: CategoryCreate) -> NoteCategory:
    """创建分类；指定父分类时校验存在性、同级同名与 3 级深度限制。"""
    cats = await _load_active(db, user_id)

    if data.parent_id is not None:
        parent = cats.get(data.parent_id)
        if parent is None:
            raise _not_found()
        if _depth_of(data.parent_id, cats) >= MAX_DEPTH:
            raise BusinessError(
                code=ErrorCode.INVALID_PARAMETER,
                message=f"分类最多 {MAX_DEPTH} 级，无法在更深一层创建",
            )

    await _assert_same_name_free(db, user_id, data.parent_id, data.name)

    cat = NoteCategory(
        id=str(uuid.uuid4()),
        user_id=user_id,
        parent_id=data.parent_id,
        name=data.name,
        sort_order=await _next_sort_order(db, user_id, data.parent_id),
        icon=data.icon,
        color=data.color,
    )
    db.add(cat)
    await db.flush()
    return cat


async def update_category(
    db: AsyncSession, user_id: str, category_id: str, data: CategoryUpdate
) -> NoteCategory:
    """重命名 / 修改图标颜色。"""
    cats = await _load_active(db, user_id)
    cat = cats.get(category_id)
    if cat is None:
        raise _not_found()

    await _assert_same_name_free(db, user_id, cat.parent_id, data.name, exclude_id=category_id)
    cat.name = data.name
    cat.icon = data.icon
    cat.color = data.color
    await db.flush()
    return cat


async def move_category(
    db: AsyncSession, user_id: str, category_id: str, new_parent_id: str | None
) -> NoteCategory:
    """移动分类到新的父分类；校验环（不能移到自己或自己的子孙）与深度。"""
    cats = await _load_active(db, user_id)
    cat = cats.get(category_id)
    if cat is None:
        raise _not_found()

    if new_parent_id == category_id:
        raise BusinessError(code=ErrorCode.INVALID_PARAMETER, message="不能移动到自身")

    if new_parent_id is not None:
        new_parent = cats.get(new_parent_id)
        if new_parent is None:
            raise _not_found()
        if _is_descendant(new_parent_id, category_id, cats):
            raise BusinessError(
                code=ErrorCode.INVALID_PARAMETER, message="不能移动到自己的子分类下（会形成环）"
            )
        new_depth = _depth_of(new_parent_id, cats) + 1
        if new_depth + _subtree_height(category_id, cats) - 1 > MAX_DEPTH:
            raise BusinessError(
                code=ErrorCode.INVALID_PARAMETER,
                message=f"移动后子树将超过 {MAX_DEPTH} 级深度限制",
            )

    if new_parent_id != cat.parent_id:
        await _assert_same_name_free(db, user_id, new_parent_id, cat.name, exclude_id=category_id)

    cat.parent_id = new_parent_id
    cat.sort_order = await _next_sort_order(db, user_id, new_parent_id)
    await db.flush()
    return cat


async def _load_deleted(db: AsyncSession, user_id: str, category_id: str) -> NoteCategory:
    cat = (
        await db.execute(
            select(NoteCategory).where(
                NoteCategory.id == category_id,
                NoteCategory.user_id == user_id,
                NoteCategory.deleted_at.isnot(None),
            )
        )
    ).scalar_one_or_none()
    if cat is None:
        raise _not_found()
    return cat


async def _promote_active_children(db: AsyncSession, cat: NoteCategory) -> None:
    """物理删除前把仍活跃的直接子分类提升为顶级，避免 CASCADE 误删。"""
    children = (
        await db.execute(
            select(NoteCategory).where(
                NoteCategory.parent_id == cat.id,
                NoteCategory.user_id == cat.user_id,
                NoteCategory.deleted_at.is_(None),
            )
        )
    ).scalars().all()
    if not children:
        return
    base = await _next_sort_order(db, cat.user_id, None)
    for i, child in enumerate(children):
        child.parent_id = None
        child.sort_order = base + i
    await db.flush()


async def soft_delete_category(db: AsyncSession, user_id: str, category_id: str) -> dict:
    """软删除分类：活跃子分类提升到其父级，直属笔记变为未分类。"""
    cats = await _load_active(db, user_id)
    cat = cats.get(category_id)
    if cat is None:
        raise _not_found()

    now = datetime.now()
    promoted = 0
    for child in cats.values():
        if child.parent_id == category_id:
            child.parent_id = cat.parent_id
            promoted += 1

    note_count = (
        await db.execute(
            select(func.count(Note.id)).where(
                Note.category_id == category_id,
                Note.user_id == user_id,
                Note.deleted_at.is_(None),
            )
        )
    ).scalar_one()
    await db.execute(
        Note.__table__.update()
        .where(Note.category_id == category_id, Note.user_id == user_id)
        .values(category_id=None)
    )
    cat.deleted_at = now
    await db.flush()
    return {"subcategory_count": promoted, "note_count": note_count}


async def restore_category(db: AsyncSession, user_id: str, category_id: str) -> dict:
    """恢复分类，并拉回已删除的祖先，保证 parent_id 链完整。"""
    cat = await _load_deleted(db, user_id, category_id)
    to_restore: list[NoteCategory] = [cat]
    current_id = cat.parent_id
    while current_id:
        ancestor = (
            await db.execute(
                select(NoteCategory).where(
                    NoteCategory.id == current_id,
                    NoteCategory.user_id == user_id,
                )
            )
        ).scalar_one_or_none()
        if ancestor is None:
            break
        if ancestor.deleted_at is not None:
            to_restore.append(ancestor)
        current_id = ancestor.parent_id

    all_cats = (
        await db.execute(select(NoteCategory).where(NoteCategory.user_id == user_id))
    ).scalars().all()
    children_map: dict[str | None, list[NoteCategory]] = defaultdict(list)
    for item in all_cats:
        children_map[item.parent_id].append(item)

    def collect_deleted_children(node: NoteCategory) -> None:
        for child in children_map.get(node.id, []):
            if child.deleted_at is not None:
                to_restore.append(child)
                collect_deleted_children(child)

    collect_deleted_children(cat)

    seen: set[str] = set()
    unique: list[NoteCategory] = []
    for item in to_restore:
        if item.id in seen:
            continue
        seen.add(item.id)
        unique.append(item)

    for item in unique:
        await _assert_same_name_free(db, user_id, item.parent_id, item.name, exclude_id=item.id)
        item.deleted_at = None
    await db.flush()
    return {"restored_count": len(unique)}


async def permanent_delete_category(db: AsyncSession, user_id: str, category_id: str) -> dict:
    cat = await _load_deleted(db, user_id, category_id)
    await _promote_active_children(db, cat)
    name = cat.name
    await db.delete(cat)
    await db.flush()
    return {"deleted_name": name}


async def list_recycle_bin(db: AsyncSession, user_id: str) -> dict:
    deleted = list(
        (
            await db.execute(
                select(NoteCategory)
                .where(NoteCategory.user_id == user_id, NoteCategory.deleted_at.isnot(None))
                .order_by(NoteCategory.deleted_at.desc())
            )
        ).scalars().all()
    )
    children_map: dict[str | None, list[NoteCategory]] = defaultdict(list)
    for cat in deleted:
        children_map[cat.parent_id].append(cat)

    def count_descendants(node: NoteCategory) -> int:
        kids = children_map.get(node.id, [])
        return len(kids) + sum(count_descendants(child) for child in kids)

    days = get_settings().recycle_bin_cleanup_days
    now = datetime.now()
    items = []
    for cat in deleted:
        elapsed = (now - cat.deleted_at).days if cat.deleted_at else 0
        items.append(
            {
                "id": cat.id,
                "name": cat.name,
                "icon": cat.icon,
                "color": cat.color,
                "parent_id": cat.parent_id,
                "deleted_at": cat.deleted_at,
                "days_remaining": max(0, days - elapsed),
                "descendant_count": count_descendants(cat),
            }
        )
    return {"categories": items, "total": len(items)}


async def reorder_categories(
    db: AsyncSession, user_id: str, data: CategoryReorderRequest
) -> None:
    cats = await _load_active(db, user_id)
    if data.parent_id is not None and data.parent_id not in cats:
        raise _not_found()
    siblings = {
        cat.id
        for cat in cats.values()
        if cat.parent_id == data.parent_id
    }
    if set(data.ordered_ids) != siblings:
        raise BusinessError(code=ErrorCode.INVALID_PARAMETER, message="排序列表与当前同级分类不匹配")
    for i, cat_id in enumerate(data.ordered_ids):
        cats[cat_id].sort_order = i
    await db.flush()


async def merge_categories(
    db: AsyncSession, user_id: str, source_ids: list[str], target_id: str
) -> dict:
    source_ids = list(dict.fromkeys(source_ids))
    cats = await _load_active(db, user_id)
    target = cats.get(target_id)
    if target is None:
        raise _not_found()
    if target_id in source_ids:
        raise BusinessError(code=ErrorCode.INVALID_PARAMETER, message="合并目标不能是待操作分类自身")

    sources: list[NoteCategory] = []
    for sid in source_ids:
        cat = cats.get(sid)
        if cat is None:
            raise _not_found()
        if _is_descendant(target_id, sid, cats):
            raise BusinessError(code=ErrorCode.INVALID_PARAMETER, message="合并目标不能是源分类的子孙")
        for other in sources:
            if _is_descendant(sid, other.id, cats) or _is_descendant(other.id, sid, cats):
                raise BusinessError(
                    code=ErrorCode.INVALID_PARAMETER, message="批量合并不能包含父子关系"
                )
        sources.append(cat)

    target_depth = _depth_of(target_id, cats)
    for cat in sources:
        if target_depth + _subtree_height(cat.id, cats) - 1 > MAX_DEPTH:
            raise BusinessError(
                code=ErrorCode.INVALID_PARAMETER,
                message=f"合并后分类「{cat.name}」的子树将超过 {MAX_DEPTH} 级",
            )

    for cat in sources:
        for child in cats.values():
            if child.parent_id == cat.id:
                await _assert_same_name_free(db, user_id, target_id, child.name, exclude_id=child.id)

    await db.execute(
        update(Note)
        .where(Note.user_id == user_id, Note.category_id.in_(source_ids))
        .values(category_id=target_id)
    )
    base = await _next_sort_order(db, user_id, target_id)
    moved = [c for c in cats.values() if c.parent_id in set(source_ids)]
    moved.sort(key=lambda item: item.sort_order)
    for i, child in enumerate(moved):
        child.parent_id = target_id
        child.sort_order = base + i

    now = datetime.now()
    for cat in sources:
        cat.deleted_at = now
    await db.flush()
    return {"merged_count": len(sources), "target_id": target_id}


async def cleanup_expired_categories(db: AsyncSession, days: int | None = None) -> int:
    cutoff = datetime.now() - timedelta(days=days or get_settings().recycle_bin_cleanup_days)
    expired = list(
        (
            await db.execute(
                select(NoteCategory).where(
                    NoteCategory.deleted_at.isnot(None),
                    NoteCategory.deleted_at <= cutoff,
                )
            )
        ).scalars().all()
    )
    for cat in expired:
        await _promote_active_children(db, cat)
        await db.delete(cat)
    await db.flush()
    return len(expired)
