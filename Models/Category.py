from pydantic import BaseModel, Field, model_validator
from typing import Optional,List
from datetime import datetime
import json

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

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value