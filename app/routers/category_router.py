"""分类路由。

- GET    /category/tree
- POST   /category
- PUT    /category/{id}
- POST   /category/{id}/move
- DELETE /category/{id}                 软删除（活跃子分类提升）
- GET    /category/recycle-bin
- POST   /category/{id}/restore         级联恢复祖先
- DELETE /category/{id}/permanent
- POST   /category/reorder
- POST   /category/batch                delete / merge / restore / permanent_delete
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.failed_response import BusinessError, ErrorCode
from app.core.success_response import success_response
from app.db.database import get_db_session
from app.schemas.category import (
    CategoryBatchRequest,
    CategoryCreate,
    CategoryMoveRequest,
    CategoryReorderRequest,
    CategoryUpdate,
)
from app.services import category_service
from app.utils.auth_utils import get_current_user_id

router = APIRouter()


@router.get("/category/tree", summary="获取分类树")
async def category_tree(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    return success_response(data=await category_service.get_category_tree(db, user_id))


@router.post("/category", summary="创建分类")
async def create_category(
    data: CategoryCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    cat = await category_service.create_category(db, user_id, data)
    detail = await category_service.get_category_dict(db, user_id, cat.id)
    return success_response(data=detail)


@router.put("/category/{category_id}", summary="更新分类")
async def update_category(
    category_id: str,
    data: CategoryUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    await category_service.update_category(db, user_id, category_id, data)
    detail = await category_service.get_category_dict(db, user_id, category_id)
    return success_response(data=detail)


@router.post("/category/{category_id}/move", summary="移动分类")
async def move_category(
    category_id: str,
    data: CategoryMoveRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    await category_service.move_category(db, user_id, category_id, data.parent_id)
    detail = await category_service.get_category_dict(db, user_id, category_id)
    return success_response(data=detail)


@router.delete("/category/{category_id}", summary="删除分类")
async def delete_category(
    category_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    impact = await category_service.soft_delete_category(db, user_id, category_id)
    return success_response(data=impact, message="分类已删除")


@router.get("/category/recycle-bin", summary="回收站分类列表")
async def recycle_bin(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    return success_response(data=await category_service.list_recycle_bin(db, user_id))


@router.post("/category/{category_id}/restore", summary="恢复分类")
async def restore_category(
    category_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    result = await category_service.restore_category(db, user_id, category_id)
    return success_response(data=result, message="分类已恢复")


@router.delete("/category/{category_id}/permanent", summary="彻底删除分类")
async def permanent_delete_category(
    category_id: str,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    result = await category_service.permanent_delete_category(db, user_id, category_id)
    return success_response(data=result, message="分类已彻底删除")


@router.post("/category/reorder", summary="批量重排分类")
async def reorder_categories(
    data: CategoryReorderRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    await category_service.reorder_categories(db, user_id, data)
    return success_response(message="排序已更新")


@router.post("/category/batch", summary="批量操作分类")
async def batch_operation(
    data: CategoryBatchRequest,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    if data.operation == "delete":
        total_notes = 0
        total_subs = 0
        for cid in data.category_ids:
            impact = await category_service.soft_delete_category(db, user_id, cid)
            total_notes += impact["note_count"]
            total_subs += impact["subcategory_count"]
        return success_response(
            data={
                "operation": "delete",
                "total": len(data.category_ids),
                "subcategory_count": total_subs,
                "note_count": total_notes,
            },
            message=f"批量删除完成：{len(data.category_ids)} 个分类",
        )

    if data.operation == "merge":
        if not data.merge_target_id:
            raise BusinessError(code=ErrorCode.INVALID_PARAMETER, message="merge 必须指定目标")
        result = await category_service.merge_categories(
            db, user_id, data.category_ids, data.merge_target_id
        )
        return success_response(
            data={"operation": "merge", **result},
            message=f"合并完成：{result['merged_count']} 个分类已并入目标",
        )

    success_ids: list[str] = []
    errors: list[dict] = []
    for cid in data.category_ids:
        try:
            if data.operation == "permanent_delete":
                await category_service.permanent_delete_category(db, user_id, cid)
            else:
                await category_service.restore_category(db, user_id, cid)
            success_ids.append(cid)
        except BusinessError as exc:
            errors.append({"category_id": cid, "error": exc.message})
    action = "彻底删除" if data.operation == "permanent_delete" else "恢复"
    return success_response(
        data={
            "operation": data.operation,
            "total": len(data.category_ids),
            "success_count": len(success_ids),
            "error_count": len(errors),
            "errors": errors or None,
        },
        message=f"批量{action}完成：成功 {len(success_ids)} 个，失败 {len(errors)} 个",
    )
