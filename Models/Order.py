from pydantic import BaseModel, Field, model_validator, EmailStr
from typing import Optional,List
from datetime import datetime
import json

class OrderDetails(BaseModel):
    total_quantity: int
    varientArr: List[int]
    total_price: float
    discountInPercentage: int
    deliveryCharges: float
    shippingRateId: int
    discountedPrice: float
    discountAmount: float
    sale_price: float
    varient_name_arr: Optional[List[str]] = None
    stock_quantity: int
    # purchase_units: Optional[dict] = {}
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
    payment_details: Optional[dict] = None
    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

class OrderModel(BaseModel):
    # customer_id: str
    order_details: OrderDetails
    discount_id: Optional[str] = None
    getway_name: str
    # payment_details: PaymentDetails
    product_id: str
    order_tracking_id: str
    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
    
class InvoiceModel(BaseModel):
    email: Optional[List[EmailStr]] = None
    order_id: str
    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value

