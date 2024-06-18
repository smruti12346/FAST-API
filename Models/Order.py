from pydantic import BaseModel, Field, model_validator
from typing import Optional,List
from datetime import datetime
import json

class OrderDetails(BaseModel):
    total_quantity: int
    varientArr: List[int]
    total_price: int
    discountInPercentage: int
    discountedPrice: int
    discountAmount: int
    sale_price: int
    varient_name_arr: List[str]
    stock_quantity: int
    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
    
class PaymentDetails(BaseModel):
    payment_type: str
    payment_method: str
    transaction_id: str
    transaction_status: int
    payment_status: int
    payment_date: str
    payment_status_message: str
    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

class OrderModel(BaseModel):
    # customer_id: str
    order_details: OrderDetails
    payment_details: PaymentDetails
    product_id: str
    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
    
