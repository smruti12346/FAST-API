from pydantic import BaseModel, model_validator
from typing import List
import json

class CartModel(BaseModel):
    id: str
    varientArr: List[int]
    varientSuggestionArr: List[object]
    quantity: int

    @model_validator(mode="before")
    @classmethod
    def validate_to_json(cls, value):
        if isinstance(value, str):
            return cls(**json.loads(value))
        return value