from db import db
from bson import ObjectId

collection = db["product"]


def create(product_data):
    try:
        product_data = dict(product_data)
        if (
            collection.count_documents(
                {
                    "name": product_data["name"],
                    "category_id": int(product_data["category_id"]),
                }
            )
            > 0
        ):
            return {
                "message": "Product name with this category is already exists",
                "status": "error",
            }

        product_data["id"] = (
            int(dict(collection.find_one({}, sort=[("id", -1)]))["id"]) + 1
            if collection.find_one({}, sort=[("id", -1)]) is not None
            else 1
        )
        result = collection.insert_one(product_data)
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
            {
                "$lookup": {
                    "from": "category",
                    "localField": "category_id",
                    "foreignField": "id",
                    "as": "category",
                }
            },
            {
                "$addFields": {
                    "category": {"$arrayElemAt": ["$category", 0]},
                    "_id": {"$toString": "$_id"},
                }
            },
            {
                "$addFields": {
                    "category_name": "$category.name",
                    "category_slug": "$category.slug",
                    "category_parent_id_arr": "$category.parent_id_arr",
                    "imageUrl": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/",
                            "$cover_image",
                        ]
                    },
                    "imageUrl100": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/100/",
                            "$cover_image",
                            
                        ]
                    },
                    "imageUrl300": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/300/",
                            "$cover_image",
                            
                        ]
                    },
                    "imageArrUrl": {
                        "$map": {
                            "input": "$images",
                            "as": "image",
                            "in": {
                                "$concat": [
                                    str(request.base_url)[:-1],
                                    "/uploads/products/",
                                    "$$image",
                                ]
                            },
                        }
                    },
                    "imageArrUrl100": {
                        "$map": {
                            "input": "$images",
                            "as": "image",
                            "in": {
                                "$concat": [
                                    str(request.base_url)[:-1],
                                    "/uploads/products/100/",
                                    "$$image",
                                    
                                ]
                            },
                        }
                    },
                    "imageArrUrl300": {
                        "$map": {
                            "input": "$images",
                            "as": "image",
                            "in": {
                                "$concat": [
                                    str(request.base_url)[:-1],
                                    "/uploads/products/300/",
                                    "$$image",
                                    
                                ]
                            },
                        }
                    },
                }
            },
            {"$unset": "category"},
            {
                "$lookup": {
                    "from": "category",
                    "localField": "category_parent_id_arr",
                    "foreignField": "id",
                    "as": "parent_categories",
                }
            },
            {"$addFields": {"parent_category_names": "$parent_categories.name"}},
            {"$unset": "parent_categories"},
        ]

        result = list(collection.aggregate(pipeline))
        return {"data": result, "status": "success"}

    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_product_by_id(request, product_id):
    try:
        pipeline = [
            {"$match": {"_id": ObjectId(product_id)}},
            {
                "$lookup": {
                    "from": "category",
                    "localField": "category_id",
                    "foreignField": "id",
                    "as": "category",
                }
            },
            {
                "$addFields": {
                    "category": {"$arrayElemAt": ["$category", 0]},
                    "_id": {"$toString": "$_id"},
                }
            },
            {
                "$addFields": {
                    "category_name": "$category.name",
                    "category_slug": "$category.slug",
                    "category_parent_id_arr": "$category.parent_id_arr",
                    "imageUrl": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/",
                            "$cover_image",
                        ]
                    },
                    "imageUrl100": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/100/",
                            "$cover_image",
                            
                        ]
                    },
                    "imageUrl300": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/300/",
                            "$cover_image",
                            
                        ]
                    },
                    "imageArrUrl": {
                        "$map": {
                            "input": "$images",
                            "as": "image",
                            "in": {
                                "$concat": [
                                    str(request.base_url)[:-1],
                                    "/uploads/products/",
                                    "$$image",
                                ]
                            },
                        }
                    },
                    "imageArrUrl100": {
                        "$map": {
                            "input": "$images",
                            "as": "image",
                            "in": {
                                "$concat": [
                                    str(request.base_url)[:-1],
                                    "/uploads/products/100/",
                                    "$$image",
                                    
                                ]
                            },
                        }
                    },
                    "imageArrUrl300": {
                        "$map": {
                            "input": "$images",
                            "as": "image",
                            "in": {
                                "$concat": [
                                    str(request.base_url)[:-1],
                                    "/uploads/products/300/",
                                    "$$image",
                                    
                                ]
                            },
                        }
                    },
                }
            },
            {"$unset": "category"},
            {
                "$lookup": {
                    "from": "category",
                    "localField": "category_parent_id_arr",
                    "foreignField": "id",
                    "as": "parent_categories",
                }
            },
            {"$addFields": {"parent_category_names": "$parent_categories.name"}},
            {"$unset": "parent_categories"},
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


def delete_product(product_id: str):
    result = collection.delete_one({"_id": ObjectId(product_id)})
    if result.deleted_count == 1:
        return {"message": "data deleted successfully", "status": "success"}
    else:
        return {"message": "failed to delete", "status": "error"}
