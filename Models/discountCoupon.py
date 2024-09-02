from typing import Optional
from pydantic import BaseModel, model_validator, Field
from datetime import datetime
import json

class DiscountCouponModel(BaseModel):
    id: Optional[int] = Field(default=0)
    name: Optional[str] = None
    coupon_code: Optional[str] = None
    validity: Optional[str] = None
    value_in_percentage: Optional[float] = 0
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
    

class DiscountCouponUpdateModel(BaseModel):
    name: str
    validity: str
    value_in_percentage: float
    status: Optional[int] = Field(default=1)
    updated_at: Optional[str] = Field(default=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    updated_by: Optional[str] = None
    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value