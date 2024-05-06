from db import db
from bson import ObjectId

collection = db["category"]


def create(data):
    try:
        data = dict(data)
        data["id"] = int(dict(collection.find_one({}, sort=[("id", -1)]))["id"]) + 1 if collection.find_one({}, sort=[("id", -1)]) is not None else 1
        data["parent_id_arr"] = list(map(int, data["parent_id_arr"]))
        result = collection.insert_one(data)
        return {
            "message": "data inserted successfully",
            "_id": str(result.inserted_id),
            "status": "success",
        }
    except Exception as e:
        return {"message": e, "status": "error"}

def get_all():
    try:
        pipeline = [
            {"$match": {}},
            {"$unwind": "$parent_id_arr"},
            {
                "$lookup": {
                    "from": "product_category_productcategory",
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
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": e, "status": "error"}


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
        return {"message": e, "status": "error"}
    
def get_category_by_id(id):
    try:
        result = list(
            collection.find({"_id": ObjectId(id), "deleted_at": None})
        )
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": e, "status": "error"}
    
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
        return {"message": e, "status": "error"}


def delete_category(category_id: str):
    result = collection.delete_one({"_id": ObjectId(category_id)})
    if result.deleted_count == 1:
        return {"message": "data deleted successfully", "status": "success"}
    else:
        return {"message": "failed to delete", "status": "error"}
