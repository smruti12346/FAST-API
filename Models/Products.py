from pydantic import BaseModel, Field, model_validator
from typing import Optional, List
from datetime import datetime
import json


class ProductModel(BaseModel):
    name: str
    category_id: int
    replacement_date: int
    slug: str
    cover_image: Optional[str] = None
    images: Optional[str] = None
    description: str = None
    main_price: float
    sale_price: float
    currency: Optional[str] = None
    quantity: int
    sold_quantity: Optional[int] = Field(default=0)
    shipping_status: Optional[int] = Field(default=0)
    shipping_value: Optional[str] = None
    variant: Optional[str] = None
    seo: Optional[str] = None

    weight: Optional[float] = Field(default=0)
    weight_unit: Optional[str] = None
    height: Optional[float] = Field(default=0)
    height_unit: Optional[str] = None
    width: Optional[float] = Field(default=0)
    width_unit: Optional[str] = None
    length: Optional[float] = Field(default=0)
    length_unit: Optional[str] = None
    tag: Optional[str] = None
    tax_status: Optional[str] = None
    tax_percentage: Optional[float] = None

    status: Optional[int] = Field(default=1)
    deleted_at: Optional[str] = None
    created_at: Optional[str] = Field(
        default=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )

    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class VariantItem(BaseModel):
    varientname: str
    varient: str
    quantity: int
    price: float
    undervarient: Optional[List["VariantItem"]] = []

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value


class ProductUpdateModel(BaseModel):
    name: str
    category_id: int
    replacement_date: int
    slug: str
    cover_image: Optional[str] = None
    images: Optional[List[str]] = None
    description: str = None
    main_price: float
    sale_price: float
    currency: Optional[str] = None
    quantity: int
    variant: Optional[str] = None
    seo: Optional[str] = None

    weight: Optional[float] = Field(default=0)
    weight_unit: Optional[str] = None
    height: Optional[float] = Field(default=0)
    height_unit: Optional[str] = None
    width: Optional[float] = Field(default=0)
    width_unit: Optional[str] = None
    length: Optional[float] = Field(default=0)
    length_unit: Optional[str] = None
    tag: Optional[str] = None
    tax_status: Optional[str] = None
    tax_percentage: Optional[float] = None

    updated_at: Optional[str] = Field(
        default=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value
