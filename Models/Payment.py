from typing import List, Optional
from pydantic import BaseModel, model_validator, Field
from datetime import datetime
import json

class PaymentModel(BaseModel):
    name: str
    getway_name: str
    user_id: str
    password: str
    api_key: str
    currency: str
    return_url: str
    cancel_url: str
    status: Optional[int] = Field(default=0)
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
