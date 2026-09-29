"""分类相关 Pydantic Schema。"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, model_validator


class CategoryCreate(BaseModel):
    """创建分类请求。"""

    name: str = Field(min_length=1, max_length=100, description="分类名")
    parent_id: str | None = Field(default=None, max_length=36, description="父分类 ID，空为顶级")
    icon: str | None = Field(default=None, max_length=50, description="图标（emoji 或图标名）")
    color: str | None = Field(default=None, max_length=20, description="颜色（十六进制）")


class CategoryUpdate(BaseModel):
    """更新分类请求（重命名 / 改图标颜色）。"""

    name: str = Field(min_length=1, max_length=100, description="分类名")
    icon: str | None = Field(default=None, max_length=50)
    color: str | None = Field(default=None, max_length=20)


class CategoryMoveRequest(BaseModel):
    """移动分类请求（变更父分类）。"""

    parent_id: str | None = Field(default=None, max_length=36, description="新父分类 ID，空为顶级")


class CategoryReorderRequest(BaseModel):
    """批量重排同级分类。ordered_ids 必须覆盖该父级下全部活跃分类。"""

    parent_id: str | None = Field(default=None, max_length=36, description="父分类 ID，空为顶级")
    ordered_ids: list[str] = Field(min_length=1, description="该父级下全部分类 ID，按新顺序")


class CategoryBatchRequest(BaseModel):
    category_ids: list[str] = Field(min_length=1)
    operation: Literal["delete", "merge", "permanent_delete", "restore"]
    merge_target_id: str | None = Field(default=None, max_length=36)

    @model_validator(mode="after")
    def validate_merge(self):
        if self.operation == "merge" and not self.merge_target_id:
            raise ValueError("merge 必须指定 merge_target_id")
        if self.operation == "merge" and self.merge_target_id in self.category_ids:
            raise ValueError("合并目标不能是待操作分类自身")
        return self


class DeletedCategoryResponse(BaseModel):
    id: str
    name: str
    icon: str | None = None
    color: str | None = None
    parent_id: str | None = None
    deleted_at: datetime
    days_remaining: int
    descendant_count: int = 0
