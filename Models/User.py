from pydantic import BaseModel, Field
from typing import Optional,List
from datetime import datetime

class UserModel(BaseModel):
    email : str
    name : Optional[str] = None
    mobile : Optional[str] = None
    password : str
    dob : Optional[str] = None
    gender : Optional[int] = None
    profile_image : Optional[str] = None
    address : Optional[List[str]] = None
    bank_details : Optional[List[str]] = None
    user_type : Optional[int] = Field(default=1)
    user_permission : Optional[List[str]] = None
    status: Optional[int] = Field(default=1)
    deleted_at: Optional[str] = None
    created_at: Optional[str] = Field(default=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str