from typing import Optional
from pydantic import BaseModel, model_validator, Field
from datetime import datetime
import json


class WarentyModel(BaseModel):
    full_name: str
    email: str
    phone_number: str
    country_code: str
    state_code: str
    city_name: str
    pin_number: str
    roadName_area_colony: str
    platform_name: str
    product_id: str
    order_id: str
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

class WarentyUpdateModel(BaseModel):
    warranty_start_date: str
    warranty_end_date: str
    status: int
    description: str
    updated_at: Optional[str] = Field(default=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    updated_by: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value