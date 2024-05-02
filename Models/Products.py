from pydantic import BaseModel, Field
from typing import Optional,List
from datetime import datetime

class ProductModel(BaseModel):
    name: str
    category_id: int
    slug: str
    cover_image: str
    images: Optional[List[str]] = None
    description: str = None
    main_price: int
    sale_price: int
    currency: Optional[str] = None
    quantity: int
    sold_quantity: Optional[int] = None
    shipping_status: Optional[int] = None
    shipping_value: Optional[dict] = None
    variant: Optional[dict] = None
    seo: Optional[dict] = None
    status: Optional[int] = Field(default=1)
    deleted_at: Optional[str] = None
    created_at: Optional[str] = Field(default=str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    created_by: Optional[str] = None
    updated_at: Optional[str] = None
    updated_by: Optional[str] = None