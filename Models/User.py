from pydantic import BaseModel, Field, model_validator
from typing import Optional,List
from datetime import datetime
import json

class UserModel(BaseModel):
    email : str
    name : Optional[str] = None
    mobile : Optional[str] = None
    password : str
    dob : Optional[str] = None
    gender : Optional[int] = None
    profile_image : Optional[str] = None
    address : Optional[List[str]] = []
    bank_details : Optional[List[str]] = []
    user_type : Optional[int] = Field(default=1)
    user_permission : Optional[List[str]] = None
    description: Optional[str] = None
    status: Optional[int] = Field(default=1)
    deleted_at: Optional[str] = None
    created_at: Optional[str] = Field(default=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    created_date: Optional[str] = str(datetime.now().strftime("%Y-%m-%d"))
    created_time: Optional[str] = str(datetime.now().strftime("%H:%M:%S"))
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
    
class UserModelUpdate(BaseModel):
    name: Optional[str] = None
    mobile: Optional[str] = None
    dob: Optional[str] = None
    gender: Optional[int] = None
    profile_image: Optional[str] = None
    address: Optional[List[str]] = None
    bank_details: Optional[List[str]] = None
    user_type: Optional[int] = None
    user_permission: Optional[List[str]] = None
    description: Optional[str] = None
    status: Optional[int] = None
    deleted_at: Optional[str] = None
    updated_at: Optional[str] = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_by: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

class UserModelAddressUpdate(BaseModel):
    full_name: str 
    phone_number: str
    country_code: str
    state_code: str
    city_name: str
    pin_number: str
    roadName_area_colony: str
    house_bulding_name: str
    landmark: str
    primary_status: Optional[int] = Field(default=0)
    status: Optional[int] = Field(default=1)
    deleted_at: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class UserModelBankDetailsUpdate(BaseModel):
    upi_id: Optional[str] = None
    bank_name: str
    branch_name: str
    account_holder_name: str
    account_number: str
    ifsc_code: str
    primary_status: Optional[int] = Field(default=0)
    status: Optional[int] = Field(default=1)
    deleted_at: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

class Token(BaseModel):
    access_token: str
    token_type: str