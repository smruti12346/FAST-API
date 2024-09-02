import random
import string
from db import db
from bson import ObjectId
from datetime import datetime
from .common import paginate

collection = db["discount_coupon"]


def generate_coupon_code(length=8, use_upper=True, use_digits=True, use_symbols=False):
    characters = ""
    if use_upper:
        characters += string.ascii_uppercase
    if use_digits:
        characters += string.digits
    if use_symbols:
        characters += string.punctuation

    if not characters:
        raise ValueError("At least one character set must be enabled")

    coupon_code = "".join(random.choices(characters, k=length))
    return coupon_code


def create(data):
    try:
        data = dict(data)
        if collection.count_documents({"name": data["name"], "deleted_at": None}) != 0:
            return {"message": "Coupon name already exist", "status": "error"}

        data["id"] = (
            int(dict(collection.find_one({}, sort=[("id", -1)]))["id"]) + 1
            if collection.find_one({}, sort=[("id", -1)]) is not None
            else 1
        )
        data["coupon_code"] = generate_coupon_code(
            length=12, use_upper=True, use_digits=True, use_symbols=False
        )

        result = collection.insert_one(data)
        return {
            "message": "data inserted successfully",
            "_id": str(result.inserted_id),
            "status": "success",
        }
    except Exception as e:
        return {"message": str(e), "status": "error"}


def view(request, page, show_page):
    try:
        pipeline = [
            {"$match": {"deleted_at": None}},
            {"$sort": {"created_at": 1}},
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "deleted_at": 1,
                    "name": 1,
                    "coupon_code": 1,
                    "validity": 1,
                    "value_in_percentage": 1,
                    "status": 1,
                    "created_at": 1,
                    "created_by": 1,
                    "updated_at": 1,
                    "updated_by": 1,
                }
            },
        ]

        result = paginate(collection, pipeline, page, show_page)

        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def view_by_id(id):
    try:
        result = list(collection.find({"_id": ObjectId(id), "deleted_at": None}))
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def view_by_status(status):
    try:
        pipeline = [
            {"$match": {"status": status, "deleted_at": None}},
            {"$sort": {"created_at": 1}},
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "deleted_at": 1,
                    "name": 1,
                    "coupon_code": 1,
                    "validity": 1,
                    "value_in_percentage": 1,
                    "status": 1,
                    "created_at": 1,
                    "created_by": 1,
                    "updated_at": 1,
                    "updated_by": 1,
                }
            },
        ]
        result = collection.aggregate(pipeline)
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def view_by_coupon_code(coupon_code):
    try:
        pipeline = [
            {"$match": {"coupon_code": coupon_code, "status": 1, "deleted_at": None}},
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "deleted_at": 1,
                    "name": 1,
                    "coupon_code": 1,
                    "validity": 1,
                    "value_in_percentage": 1,
                    "status": 1,
                    "created_at": 1,
                    "created_by": 1,
                    "updated_at": 1,
                    "updated_by": 1,
                }
            },
        ]
        result = collection.aggregate(pipeline)
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def view_by_coupon_code_with_customer_id(coupon_code, customer_id):
    try:

        check_result = list(db["order"].find(
            {
                "customer_id": customer_id,
                "discount_id": coupon_code,
                "status": {"$nin": [1, 2, 3]},
            }
        ))

        if len(check_result) != 0 :
            return {"message": "Coupon code already used by customer", "status": "error"}

        pipeline = [
            {"$match": {"coupon_code": coupon_code, "status": 1, "deleted_at": None}},
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "deleted_at": 1,
                    "name": 1,
                    "coupon_code": 1,
                    "validity": 1,
                    "value_in_percentage": 1,
                    "status": 1,
                    "created_at": 1,
                    "created_by": 1,
                    "updated_at": 1,
                    "updated_by": 1,
                }
            },
        ]
        result = collection.aggregate(pipeline)
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def update(id, data):
    try:
        data = dict(data)
        result = collection.update_one({"_id": ObjectId(id)}, {"$set": data})
        if result.modified_count == 1:
            return {"message": "data updated successfully", "status": "success"}
        else:
            return {"message": "failed to update", "status": "error"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def delete(discount_id: str):
    result = collection.update_one(
        {"_id": ObjectId(discount_id)},
        {"$set": {"deleted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}},
    )
    if result.modified_count == 1:
        return {"message": "data deleted successfully", "status": "success"}
    else:
        return {"message": "failed to delete", "status": "error"}


def change_status(discount_id: str):
    getStatus = view_by_id(discount_id)["data"][0]["status"]

    if getStatus == 0:
        status = 1
    else:
        status = 0

    result = collection.update_one(
        {"_id": ObjectId(discount_id)},
        {"$set": {"status": status}},
    )
    if result.modified_count == 1:
        return {"message": "status changed successfully", "status": "success"}
    else:
        return {"message": "failed to change status", "status": "error"}
