from db import db
from fastapi import Request
from bson import ObjectId
from datetime import datetime
from .common import paginate


collection = db["wishlist"]


def create(product_id, customer_id):
    try:
        if (
            collection.count_documents(
                {
                    "product_id": product_id,
                    "customer_id": customer_id,
                    "deleted_at": None,
                }
            )
            != 0
        ):
            return {"message": "Product already exist", "status": "error"}
        data = {
            "product_id": product_id,
            "customer_id": customer_id,
            "status": 1,
            "deleted_at": None,
            "created_at": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            "created_by": None,
            "updated_at": None,
            "updated_by": None,
        }

        data["id"] = (
            int(dict(collection.find_one({}, sort=[("id", -1)]))["id"]) + 1
            if collection.find_one({}, sort=[("id", -1)]) is not None
            else 1
        )

        result = collection.insert_one(data)
        return {
            "message": "data inserted successfully",
            "_id": str(result.inserted_id),
            "status": "success",
        }
    except Exception as e:
        return {"message": str(e), "status": "error"}


def view(request, page, show_page, id):
    try:
        pipeline = [
            {"$match": {"customer_id": id, "deleted_at": None}},
            {"$sort": {"created_at": -1}},
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
                    "product_details.imageUrl100": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/100/",
                            "$product_details.cover_image",
                        ]
                    },
                    "product_details.name": "$product_details.name",
                    "product_details.slug": "$product_details.slug",
                }
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "customer_id": 1,
                    "product_id": {"$toString": "$product_id"},
                    "status": 1,
                    "product_details._id": {"$toString": "$product_details._id"},
                    "product_details.name": 1,
                    "product_details.slug": 1,
                    "product_details.imageUrl100": 1,
                    "shipping_details": 1,
                    "created_at": 1,
                }
            },
        ]

        result = paginate(collection, pipeline, page, show_page)

        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def delete(id: str):
    result = collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"deleted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}},
    )
    if result.modified_count == 1:
        return {"message": "data deleted successfully", "status": "success"}
    else:
        return {"message": "failed to delete", "status": "error"}
