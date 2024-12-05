from db import db
from bson import ObjectId
from datetime import datetime
from .common import paginate

collection = db["warenty"]


def create(data, id):
    try:
        data = dict(data)
        if (
            collection.count_documents(
                {
                    "email": data["email"],
                    "order_id": data["order_id"],
                    "deleted_at": None,
                }
            )
            != 0
        ):
            return {"message": "Order ID Already exist", "status": "error"}

        data["created_by"] = id
        result = collection.insert_one(data)
        return {
            "message": "Warenty Request sent to Admin Successfully",
            "_id": str(result.inserted_id),
            "status": "success",
        }
    except Exception as e:
        return {"message": str(e), "status": "error"}


def view(request, page, show_page):
    try:
        pipeline = [
            {"$match": {"deleted_at": None}},
            {
                "$addFields": {
                    "customer_id_obj": {"$toObjectId": "$created_by"},
                    "product_id_obj": {"$toObjectId": "$product_id"},
                }
            },
            {
                "$lookup": {
                    "from": "user",
                    "localField": "customer_id_obj",
                    "foreignField": "_id",
                    "as": "user_details",
                }
            },
            {
                "$lookup": {
                    "from": "product",
                    "localField": "product_id_obj",
                    "foreignField": "_id",
                    "as": "product_details",
                }
            },
            {"$unwind": "$user_details"},
            {"$unwind": "$product_details"},
            {"$unset": ["customer_id_obj", "product_id_obj"]},
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
                }
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "full_name": 1,
                    "email": 1,
                    "phone_number": 1,
                    "platform_name": 1,
                    "product_id": 1,
                    "order_id": 1,
                    "status": 1,
                    "created_at": 1,
                    "warranty_start_date": 1,
                    "warranty_end_date": 1,
                    "description": 1,
                    "product_details._id": {"$toString": "$product_details._id"},
                    "product_details.name": 1,
                    "product_details.slug": 1,
                    "product_details.product_sku": 1,
                    "product_details.cover_image": 1,
                    "product_details.imageUrl": 1,
                    "product_details.imageUrl100": 1,
                    "product_details.imageUrl300": 1,
                }
            },
            {"$sort": {"created_at": -1}},
        ]
        result = paginate(collection, pipeline, page, show_page)
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def update(warenty_id, data, id):
    try:
        data = dict(data)
        data['updated_by'] = id
        result = collection.update_one({"_id": ObjectId(warenty_id)}, {"$set": data})
        if result.modified_count == 1:
            return {"message": "data updated successfully", "status": "success"}
        else:
            return {"message": "failed to update", "status": "error"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


# def delete(payment_id: str):
#     result = collection.update_one(
#         {"_id": ObjectId(payment_id)},
#         {"$set": {"deleted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}},
#     )
#     if result.modified_count == 1:
#         return {"message": "data deleted successfully", "status": "success"}
#     else:
#         return {"message": "failed to delete", "status": "error"}
