from db import db
from os import getcwd
import os
import uuid
from services.common import resize_image, paginate
from fastapi import UploadFile
from bson import ObjectId

collection = db["component"]


def create_component(data):
    try:
        data = data.dict()
        if collection.count_documents({"slug": data["slug"], "deleted_at": None}) != 0:
            return {"message": "slug already exist", "status": "error"}

        result = collection.insert_one(data)
        return {
            "message": "data inserted successfully",
            "_id": str(result.inserted_id),
            "status": "success",
        }
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_component(request, page, show_page):
    try:
        pipeline = [
            {"$match": {"deleted_at": None}},
            {"$sort": {"created_at": 1}},
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "deleted_at": 1,
                    "name": 1,
                    "slug": 1,
                    "fields": 1,
                    "field_values": 1,
                    "description": 1,
                    "seo": 1,
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


def get_component_by_slug(request, slug):
    try:
        pipeline = [
    {"$match": {"slug": slug, "deleted_at": None}},
    {"$sort": {"created_at": 1}},
    {
        "$project": {
            "_id": {"$toString": "$_id"},
            "deleted_at": 1,
            "name": 1,
            "slug": 1,
            "fields": 1,
            "field_values": {
                "$map": {
                    "input": "$field_values",
                    "as": "field_value",
                    "in": {
                        "$arrayToObject": {
                            "$concatArrays": [
                                {
                                    "$map": {
                                        "input": {
                                            "$objectToArray": "$$field_value"
                                        },
                                        "as": "field_key_value",
                                        "in": {
                                            "k": "$$field_key_value.k",
                                            "v": {
                                                "$cond": {
                                                    "if": {
                                                        "$and": [
                                                            {"$eq": ["$$field_key_value.k", "image"]},
                                                            {"$eq": [{"$type": "$$field_key_value.v"}, "string"]}
                                                        ]
                                                    },
                                                    "then": "$$field_key_value.v",
                                                    "else": "$$field_key_value.v"
                                                }
                                            }
                                        }
                                    }
                                },
                                # Add dynamic image URLs only if 'image' exists as string
                                {
                                    "$cond": {
                                        "if": {"$eq": [{"$type": "$$field_value.image"}, "string"]},
                                        "then": [
                                            {"k": "imageUrl", "v": {
                                                "$concat": [
                                                    str(request.base_url)[:-1],
                                                    "/uploads/component/",
                                                    "$$field_value.image"
                                                ]
                                            }},
                                            {"k": "imageUrl100", "v": {
                                                "$concat": [
                                                    str(request.base_url)[:-1],
                                                    "/uploads/component/100/",
                                                    "$$field_value.image"
                                                ]
                                            }},
                                            {"k": "imageUrl300", "v": {
                                                "$concat": [
                                                    str(request.base_url)[:-1],
                                                    "/uploads/component/300/",
                                                    "$$field_value.image"
                                                ]
                                            }}
                                        ],
                                        "else": []
                                    }
                                }
                            ]
                        }
                    }
                }
            },
            "description": 1,
            "seo": 1,
            "status": 1,
            "created_at": 1,
            "created_by": 1,
            "updated_at": 1,
            "updated_by": 1,
            "url": str(request.base_url)[:-1] + "/uploads/component/",
            "url100": str(request.base_url)[:-1] + "/uploads/component/100/",
            "url300": str(request.base_url)[:-1] + "/uploads/component/300/",
        }
    }
]
        result = list(collection.aggregate(pipeline))
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_all_component(request):
    try:
        result = list(collection.find())
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


async def add_component_details(data_dict, id):
    try:
        new_data_dict = dict(data_dict)
        for key, value in data_dict.items():
            if hasattr(value, "filename") and hasattr(value, "file"):
                PATH_FILES = getcwd() + "/uploads/component/"
                os.makedirs(PATH_FILES, exist_ok=True)
                filename = f"{uuid.uuid1()}-{os.path.splitext(value.filename)[0]}"
                mainFileName = filename + os.path.splitext(value.filename)[1]

                with open(PATH_FILES + mainFileName, "wb") as myfile:
                    content = await value.read()
                    myfile.write(content)
                    myfile.close()
                resize_image(filename, mainFileName, PATH_FILES)
                new_data_dict[key] = filename + ".webp"

        new_data_dict["id"] = f"{uuid.uuid1()}"
        filter_query = {"_id": ObjectId(id)}
        update_query = {"$push": {"field_values": new_data_dict}}
        result = collection.update_one(filter_query, update_query)
        if result.modified_count == 1:
            return {"message": "data added successfully", "status": "success"}
        else:
            return {"message": "failed to update", "status": "error"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


async def update_component_details(data_dict, parent_id, child_id):
    try:
        new_data_dict = dict(data_dict)
        for key, value in data_dict.items():
            if hasattr(value, "filename") and hasattr(value, "file"):
                PATH_FILES = getcwd() + "/uploads/component/"
                os.makedirs(PATH_FILES, exist_ok=True)
                filename = f"{uuid.uuid1()}-{os.path.splitext(value.filename)[0]}"
                mainFileName = filename + os.path.splitext(value.filename)[1]

                with open(PATH_FILES + mainFileName, "wb") as myfile:
                    content = await value.read()
                    myfile.write(content)
                    myfile.close()
                resize_image(filename, mainFileName, PATH_FILES)
                new_data_dict[key] = filename + ".webp"

        result = collection.update_one(
            {"_id": ObjectId(parent_id), "field_values.id": child_id},
            {
                "$set": {
                    f"field_values.$.{key}": value
                    for key, value in new_data_dict.items()
                }
            },
        )
        if result.modified_count == 1:
            return {"message": "data added successfully", "status": "success"}
        else:
            return {"message": "failed to update", "status": "error"}

    except Exception as e:
        return {"message": str(e), "status": "error"}


def delete_component_details(request, _id, id):
    try:
        result = collection.update_one(
            {"_id": ObjectId(_id)}, {"$pull": {"field_values": {"id": id}}}
        )

        if result.matched_count == 0:
            return {"message": "Document not found", "status": "error"}

        if result.modified_count == 0:
            return {
                "message": "Field value not found or already deleted",
                "status": "error",
            }

        return {"message": "Field value deleted successfully", "status": "success"}

    except Exception as e:
        return {"message": str(e), "status": "error"}
