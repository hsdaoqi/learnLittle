"""笔记模板：CRUD，以及套用模板创建笔记。"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.failed_response import BusinessError, ErrorCode
from app.models.note_template import NoteTemplate
from app.schemas.note import NoteCreate
from app.schemas.template import NoteTemplateApply, NoteTemplateCreate, NoteTemplateUpdate
from app.services import note_service


def _not_found() -> BusinessError:
    return BusinessError(code=ErrorCode.TEMPLATE_NOT_FOUND, http_status=404)


def body_from_structure(structure: dict | None) -> str:
    """从 JSON 骨架取出可写入笔记的正文。"""
    if not structure:
        return ""
    for key in ("markdown", "content", "body"):
        value = structure.get(key)
        if isinstance(value, str):
            return value
    return ""


async def create_template(db: AsyncSession, user_id: str, data: NoteTemplateCreate) -> NoteTemplate:
    template = NoteTemplate(
        user_id=user_id,
        name=data.name,
        content_structure=data.content_structure,
        category=data.category,
        sort_order=data.sort_order,
    )
    db.add(template)
    await db.flush()
    await db.refresh(template)
    return template


async def list_templates(db: AsyncSession, user_id: str) -> list[NoteTemplate]:
    result = await db.execute(
        select(NoteTemplate)
        .where(NoteTemplate.user_id == user_id)
        .order_by(NoteTemplate.sort_order.asc(), NoteTemplate.created_at.desc())
    )
    return list(result.scalars().all())


async def get_template(db: AsyncSession, user_id: str, template_id: int) -> NoteTemplate:
    template = (
        await db.execute(
            select(NoteTemplate).where(
                NoteTemplate.id == template_id,
                NoteTemplate.user_id == user_id,
            )
        )
    ).scalar_one_or_none()
    if template is None:
        raise _not_found()
    return template


async def update_template(
    db: AsyncSession, user_id: str, template_id: int, data: NoteTemplateUpdate
) -> NoteTemplate:
    template = await get_template(db, user_id, template_id)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(template, key, value)
    await db.flush()
    await db.refresh(template)
    return template


async def delete_template(db: AsyncSession, user_id: str, template_id: int) -> None:
    template = await get_template(db, user_id, template_id)
    await db.delete(template)
    await db.flush()


async def apply_template(
    db: AsyncSession, user_id: str, template_id: int, data: NoteTemplateApply
):
    """套用模板新建笔记：标题默认用模板名，正文取 content_structure.markdown。"""
    template = await get_template(db, user_id, template_id)
    note = await note_service.create_note(
        db,
        user_id,
        NoteCreate(
            title=data.title or template.name,
            content=body_from_structure(template.content_structure),
            category_id=data.category_id,
            format=data.format,
        ),
    )
    return note
