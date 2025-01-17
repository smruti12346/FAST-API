from db import db
from bson import ObjectId
from datetime import datetime
from .common import paginate

collection = db["newLetter"]


def create(data):
    try:
        data = dict(data)
        collection.insert_one(data)
        return {
            "message": "data inserted successfully",
            "status": "success",
        }
    except Exception as e:
        return {"message": str(e), "status": "error"}


def view(page, show_page):
    try:
        pipeline = [
            {"$match": {"deleted_at": None}},
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "name": 1,
                    "email": 1,
                    "feedback": 1,
                    "status": 1,
                    "created_at": 1,
                }
            },
        ]
        result = paginate(collection, pipeline, page, show_page)
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def view_by_status(status):
    try:
        pipeline = [
            {"$match": {"status": status, "deleted_at": None}},
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "name": 1,
                    "email": 1,
                    "feedback": 1,
                    "status": 1,
                    "created_at": 1,
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


def delete(id: str):
    result = collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"deleted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}},
    )
    if result.modified_count == 1:
        return {"message": "data deleted successfully", "status": "success"}
    else:
        return {"message": "failed to delete", "status": "error"}


def change_status(id: str):
    getStatus = view_by_id(id)["data"][0]["status"]

    if getStatus == 0:
        collection.update_many({}, {"$set": {"status": 0}})
        status = 1
    else:
        status = 0

    result = collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": {"status": status}},
    )
    if result.modified_count == 1:
        return {"message": "status changed successfully", "status": "success"}
    else:
        return {"message": "failed to change status", "status": "error"}
