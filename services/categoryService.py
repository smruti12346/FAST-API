from db import db
from bson import ObjectId
from datetime import datetime
from fastapi import Request


collection = db["category"]


def create(data):
    try:
        data = dict(data)
        data["id"] = (
            int(dict(collection.find_one({}, sort=[("id", -1)]))["id"]) + 1
            if collection.find_one({}, sort=[("id", -1)]) is not None
            else 1
        )
        data["parent_id_arr"] = list(map(int, data["parent_id_arr"]))
        result = collection.insert_one(data)
        return {
            "message": "data inserted successfully",
            "_id": str(result.inserted_id),
            "status": "success",
        }
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_all(request):
    try:
        pipeline = [
            {"$match": {"deleted_at": None}},
            {"$unwind": "$parent_id_arr"},
            {
                "$lookup": {
                    "from": "category",
                    "localField": "parent_id_arr",
                    "foreignField": "id",
                    "as": "parent_docs",
                }
            },
            {
                "$group": {
                    "_id": "$_id",
                    "id": {"$first": "$id"},
                    "parent_id": {"$first": "$parent_id"},
                    "parent_id_arr": {"$push": "$parent_id_arr"},
                    "parent_arr": {"$push": {"$arrayElemAt": ["$parent_docs.name", 0]}},
                    "name": {"$first": "$name"},
                    "slug": {"$first": "$slug"},
                    "image": {"$first": "$image"},
                    "description": {"$first": "$description"},
                    "variant": {"$first": "$variant"},
                    "seo": {"$first": "$seo"},
                    "status": {"$first": "$status"},
                    "sub_category": {"$first": "$sub_category"},
                    "step": {"$first": "$step"},
                    "deleted_at": {"$first": "$deleted_at"},
                    "created_by": {"$first": "$created_by"},
                    "created_at": {"$first": "$created_at"},
                }
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "id": 1,
                    "parent_id": 1,
                    "parent_id_arr": 1,
                    "parent_arr": 1,
                    "name": 1,
                    "slug": 1,
                    "image": 1,
                    "description": 1,
                    "variant": 1,
                    "seo": 1,
                    "status": 1,
                    "sub_category": 1,
                    "step": 1,
                    "deleted_at": 1,
                    "created_by": 1,
                    "created_at": 1,
                }
            },
            {"$sort": {"created_at": 1}},
        ]

        result = list(collection.aggregate(pipeline))
        data = []
        for doc in result:
            doc["imageUrl"] = f"{str(request.base_url)[:-1]}/uploads/category/{doc['image']}"
            doc["imageUrl100"] = f"{str(request.base_url)[:-1]}/uploads/category/100/{doc['image']}.webp"
            doc["imageUrl300"] = f"{str(request.base_url)[:-1]}/uploads/category/300/{doc['image']}.webp"
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_category_by_parent_id(parrent_id):
    try:
        result = list(
            collection.find({"parent_id": int(parrent_id), "deleted_at": None})
        )
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_category_by_id(id):
    try:
        result = list(collection.find({"_id": ObjectId(id), "deleted_at": None}))
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get(id):
    return list(collection.find({"_id": ObjectId(id), "deleted_at": None}))


def update(id, data):
    try:
        data = dict(data)
        data["parent_id_arr"] = list(map(int, data["parent_id_arr"]))
        result = collection.update_one({"_id": ObjectId(id)}, {"$set": data})
        if result.modified_count == 1:
            return {"message": "data updated successfully", "status": "success"}
        else:
            return {"message": "failed to update", "status": "error"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def change_category_status(category_id: str):
    getStatus = get(category_id)[0]["status"]
    if getStatus == 0:
        status = 1
    else:
        status = 0

    result = collection.update_one(
        {"_id": ObjectId(category_id)},
        {"$set": {"status": status}},
    )
    if result.modified_count == 1:
        return {"message": "status changed successfully", "status": "success"}
    else:
        return {"message": "failed to change status", "status": "error"}


def delete_category(category_id: str):
    # result = collection.delete_one({"_id": ObjectId(category_id)})
    result = collection.update_one(
        {"_id": ObjectId(category_id)},
        {"$set": {"deleted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}},
    )
    # if result.deleted_count == 1:
    if result.modified_count == 1:
        return {"message": "data deleted successfully", "status": "success"}
    else:
        return {"message": "failed to delete", "status": "error"}
