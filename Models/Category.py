from pydantic import BaseModel, Field
from typing import Optional,List
from datetime import datetime

class CategoryModel(BaseModel):
    parent_id: int
    parent_id_arr: str
    name: str
    slug: str
    image: Optional[str] = None
    description: Optional[str] = None
    variant: Optional[str] = None
    seo: Optional[str] = None
    status: Optional[int] = Field(default=1)
    deleted_at: Optional[str] = None
    created_at: Optional[str] = Field(default=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None
