from db import db
from bson import ObjectId
from .userService import get_user_by_id
from .productService import get_product_details_by_id, get_product_by_id
from datetime import datetime
from bson import ObjectId
import logging
import services.shippingService as shippingService

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
            "product_id": product_id,
            "order_details": {
                "total_quantity": 1,
            },
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
        pipeline = [
            {"$match": {"customer_id": user_id}},
            {"$addFields": {"product_id_obj": {"$toObjectId": "$product_id"}}},
            {
                "$lookup": {
                    "from": "product",
                    "localField": "product_id_obj",
                    "foreignField": "_id",
                    "as": "product_details",
                }
            },
            {"$unwind": "$product_details"},
            {
                "$addFields": {
                    "product_details.imageUrl": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/",
                            "$product_details.cover_image",
                        ]
                    },
                    "product_details.imageUrl100": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/100/",
                            "$product_details.cover_image",
                        ]
                    },
                    "product_details.imageUrl300": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/300/",
                            "$product_details.cover_image",
                        ]
                    },
                    "product_details.main_price": "$product_details.main_price",
                    "product_details.sale_price": "$product_details.sale_price",
                    "product_details.quantity": "$product_details.quantity",
                }
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "customer_id": 1,
                    "product_id": {"$toString": "$product_id"},
                    "order_details": 1,
                    "product_details._id": {"$toString": "$product_details._id"},
                    "product_details.name": 1,
                    "product_details.cover_image": 1,
                    "product_details.imageUrl": 1,
                    "product_details.imageUrl100": 1,
                    "product_details.imageUrl300": 1,
                    "product_details.main_price": 1,
                    "product_details.sale_price": 1,
                    "product_details.quantity": 1,
                }
            },
        ]

        result = list(collection.aggregate(pipeline))
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_cart_details_by_product_id_user_id(product_id: str, user_id: str):
    try:
        result = collection.find({"product_id": product_id, "customer_id": user_id})
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_cart_details_by_product_arr(request, items):
    try:
        data = []
        for item in items:
            product_data = get_product_by_id(request, item)
            if product_data["data"] and len(product_data["data"]) > 0:
                data.append(product_data["data"][0])
        
        AdminShipingDetails = shippingService.view_by_status(1)
        amount_for_free_shipping = 5000
        if (
            AdminShipingDetails["status"] == "success"
            and len(AdminShipingDetails["data"]) > 0
        ):
            amount_for_free_shipping = AdminShipingDetails["data"][0][
                "amount_for_free_shipping"
            ]
        
        return {"data": data, "amount_for_free_shipping": amount_for_free_shipping, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}