from typing import List, Optional
from pydantic import BaseModel, model_validator, Field
from datetime import datetime
import json

class ShippingModel(BaseModel):
    name: str
    shipping_company_name: str
    user_id: str
    password: str
    api_key: str
    currency: str
    country_code: str
    national_fix_amount: float
    international_fix_amount: float
    charges_above_national_fix_amount: float
    charges_bellow_national_fix_amount: float
    charges_above_international_fix_amount: float
    charges_bellow_international_fix_amount: float
    address_id: int
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

class ShippingUpdateModel(BaseModel):
    name: str
    shipping_company_name: str
    user_id: str
    password: str
    api_key: str
    currency: str
    country_code: str
    national_fix_amount: float
    international_fix_amount: float
    charges_above_national_fix_amount: float
    charges_bellow_national_fix_amount: float
    charges_above_international_fix_amount: float
    charges_bellow_international_fix_amount: float
    address_id: int
    status: Optional[int] = Field(default=1)
    updated_at: Optional[str] = Field(default=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    updated_by: Optional[str] = None
    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
