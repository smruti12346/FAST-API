from typing import Optional
from pydantic import BaseModel, model_validator, Field
from datetime import datetime
import json

class TaxModel(BaseModel):
    country_code: str
    national_tax_percentage: float
    international_tax_percentage: float
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