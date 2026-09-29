"""模型包：导入即把所有表注册到 Base.metadata，供 Alembic 使用。"""

from app.models.base import Base
from app.models.category import NoteCategory
from app.models.chat import ChatMessage, ChatSession, ChatSummary
from app.models.knowledge import KnowledgeDocument
from app.models.note import Note
from app.models.note_template import NoteTemplate
from app.models.review import ReviewRecord
from app.models.usage import ModelPricing, ModelTrace
from app.models.user import User

__all__ = [
    "Base",
    "ChatMessage",
    "ChatSession",
    "ChatSummary",
    "KnowledgeDocument",
    "ModelPricing",
    "ModelTrace",
    "Note",
    "NoteCategory",
    "NoteTemplate",
    "ReviewRecord",
    "User",
]
