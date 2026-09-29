"""笔记模板路由。

- POST   /note-template
- GET    /note-template
- GET    /note-template/{id}
- PUT    /note-template/{id}
- DELETE /note-template/{id}
- POST   /note-template/{id}/apply   套用模板新建笔记
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.success_response import success_response
from app.db.database import get_db_session
from app.schemas.template import (
    NoteTemplateApply,
    NoteTemplateCreate,
    NoteTemplateResponse,
    NoteTemplateUpdate,
)
from app.services import note_template_service
from app.utils.auth_utils import get_current_user_id

router = APIRouter()


def _dump(template) -> dict:
    return NoteTemplateResponse.model_validate(template).model_dump(mode="json")


@router.post("/note-template", summary="创建模板")
async def create_template(
    data: NoteTemplateCreate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    template = await note_template_service.create_template(db, user_id, data)
    return success_response(data=_dump(template))


@router.get("/note-template", summary="模板列表")
async def list_templates(
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    templates = await note_template_service.list_templates(db, user_id)
    return success_response(data={"templates": [_dump(item) for item in templates]})


@router.get("/note-template/{template_id}", summary="模板详情")
async def get_template(
    template_id: int,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    template = await note_template_service.get_template(db, user_id, template_id)
    return success_response(data=_dump(template))


@router.put("/note-template/{template_id}", summary="更新模板")
async def update_template(
    template_id: int,
    data: NoteTemplateUpdate,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    template = await note_template_service.update_template(db, user_id, template_id, data)
    return success_response(data=_dump(template))


@router.delete("/note-template/{template_id}", summary="删除模板")
async def delete_template(
    template_id: int,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    await note_template_service.delete_template(db, user_id, template_id)
    return success_response(message="模板已删除")


@router.post("/note-template/{template_id}/apply", summary="套用模板新建笔记")
async def apply_template(
    template_id: int,
    data: NoteTemplateApply,
    user_id: str = Depends(get_current_user_id),
    db: AsyncSession = Depends(get_db_session),
):
    note = await note_template_service.apply_template(db, user_id, template_id, data)
    return success_response(
        data={"id": note.id, "title": note.title, "format": note.format, "created_at": note.created_at}
    )
