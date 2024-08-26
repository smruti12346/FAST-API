import easypost
import json
import services.locationService as locationService
from services import orderService
from db import db
from bson import ObjectId
from datetime import datetime
from .common import paginate

import services.paymentService as paymentService

api_key = "2TDp15wsUbcC95Z42Y4BrQ"
client = easypost.EasyPostClient(api_key)

collection = db["tax"]


def create(data, id):
    try:
        data = dict(data)
        if collection.count_documents({"deleted_at": None}) != 0:
            return {"message": "You can add only one tax details", "status": "error"}

        data["created_by"] = id
        result = collection.insert_one(data)
        return {
            "message": "data inserted successfully",
            "_id": str(result.inserted_id),
            "status": "success",
        }
    except Exception as e:
        return {"message": str(e), "status": "error"}


def view(page, show_page):
    try:
        pipeline = [
            {"$match": {"deleted_at": None}},
            {
                "$lookup": {
                    "from": "location",
                    "localField": "country_code",
                    "foreignField": "iso2",
                    "as": "addressDetails",
                }
            },
            {"$unwind": "$addressDetails"},
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "country_code": 1,
                    "addressDetails.name": 1,
                    "national_tax_percentage": 1,
                    "international_tax_percentage": 1,
                    "status": 1,
                    "created_at": 1,
                }
            },
        ]
        result = paginate(collection, pipeline, page, show_page)

        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def viewTax():
    try:
        pipeline = [
            {"$match": {"deleted_at": None}},
            {
                "$lookup": {
                    "from": "location",
                    "localField": "country_code",
                    "foreignField": "iso2",
                    "as": "addressDetails",
                }
            },
            {"$unwind": "$addressDetails"},
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "country_code": 1,
                    "addressDetails.name": 1,
                    "national_tax_percentage": 1,
                    "international_tax_percentage": 1,
                    "status": 1,
                    "created_at": 1,
                }
            },
        ]
        result = list(collection.aggregate(pipeline))
        return {"data": result, "status": "success"}
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


def delete(payment_id: str):
    result = collection.update_one(
        {"_id": ObjectId(payment_id)},
        {"$set": {"deleted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}},
    )
    if result.modified_count == 1:
        return {"message": "data deleted successfully", "status": "success"}
    else:
        return {"message": "failed to delete", "status": "error"}
