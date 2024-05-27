from db import db
from bson import ObjectId
from .userService import get_user_by_id
from .productService import get_product_details_by_id,get_product_by_id
from datetime import datetime

collection = db["cart"]


def add_to_cart(user_id, product_id):
    try:

        order_data = get_cart_details_by_product_id_user_id(product_id, user_id)
        if order_data["data"] and len(order_data["data"]) > 0:
            return {"message": "Product already in cart", "status": "error"}

        product_data = get_product_details_by_id(product_id)
        if product_data["data"] and len(product_data["data"]) == 0:
            return {"message": "Invalid product", "status": "error"}

        user_data = get_user_by_id(user_id)
        if user_data["data"] and len(user_data["data"]) == 0:
            return {"message": "Invalid user", "status": "error"}

        cart_data = {
            "customer_id": user_id,
            "location": {},
            "contact": {
                "mobile": user_data["data"][0]["mobile"],
                "email": user_data["data"][0]["email"],
            },
            "product_id": product_id,
            "currency_id": "INR",
            "order_details": {
                "order_quantity": 1,
            },
            "payment_info": {},
            "order_tracking_id": 1,
            "status": 1,
            "deleted_at": None,
            "created_by": user_id,
            "updated_by": None,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "updated_at": None,
        }

        result = collection.insert_one(cart_data)
        return {
            "message": "data inserted successfully",
            "_id": str(result.inserted_id),
            "status": "success",
        }
    except Exception as e:
        return {"message": str(e), "status": "success"}


def get_cart_details_by_product_id(product_id: str):
    try:
        result = collection.find({"product_id": product_id})
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}

def get_all_cart_details_by_user_id(request, user_id: str):
    try:
        result = collection.find({"customer_id": user_id})
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            doc["product_details"] = get_product_by_id(request, doc["product_id"])['data'][0] if 'data' in get_product_by_id(request, doc["product_id"]) else []
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}

def get_cart_details_by_product_id_user_id(product_id: str, user_id:str):
    try:
        result = collection.find({"product_id": product_id, "customer_id": user_id})
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}
    

