from db import db
from bson import ObjectId
from .common import paginate
import re
import pymongo
from os import getcwd
import os
import uuid
from services.common import resize_image
from pydantic import Field
from datetime import datetime

collection = db["product"]


def generate_sku(product_name, unique_id):
    cleaned_name = re.sub(r"[^a-zA-Z0-9\s]", "", product_name)
    words = cleaned_name.split()
    abbreviation = "".join(word[0].upper() for word in words)
    sku = f"{abbreviation} {unique_id}"
    return sku


def create(product_data):
    try:
        product_data = dict(product_data)
        product_slug_count = collection.count_documents(
            {"slug": product_data["slug"], "deleted_at": None}
        )
        if product_slug_count != 0:
            return {"message": "slug already exist", "status": "error"}

        product_name_count = collection.count_documents(
            {
                "name": product_data["name"],
                "category_id": int(product_data["category_id"]),
            }
        )
        if product_name_count > 0:
            return {
                "message": "Product name with this category is already exists",
                "status": "error",
            }

        latest_product = collection.find_one(
            {}, sort=[("product_id", pymongo.DESCENDING)]
        )
        if latest_product and "product_id" in latest_product:
            unique_id = int(latest_product["product_id"]) + 1
        else:
            unique_id = 1

        product_data["product_id"] = int(unique_id)
        product_data["product_sku"] = generate_sku(product_data["name"], unique_id)

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
            {"$match": {"deleted_at": None}},
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


def get_all_product(request, page, show_page, search_query):
    try:
        pipeline = [{"$match": {"deleted_at": None}}]
        if search_query:
            search_condition = {
                "$or": [
                    {"name": {"$regex": search_query, "$options": "i"}},
                    {"slug": {"$regex": search_query, "$options": "i"}},
                    {"product_sku": {"$regex": search_query, "$options": "i"}},
                    {"description": {"$regex": search_query, "$options": "i"}},
                ]
            }
            try:
                search_condition["$or"].append({"_id": ObjectId(search_query)})
            except Exception:
                pass
            pipeline.append({"$match": search_condition})

        pipeline += [
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

        # result = list(collection.aggregate(pipeline))
        documents = paginate(collection, pipeline, page, show_page)
        return {"data": documents, "status": "success"}

    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_products_slugs_wise(request, slugs):
    try:
        import ast
        pipeline = [
            {
                "$match": {
                    "deleted_at": None,
                    "slug": {"$in": ast.literal_eval(slugs)},
                }
            },
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
        # documents = paginate(collection, pipeline, page, show_page)
        return {"data": result, "status": "success"}

    except Exception as e:
        return {"message": str(e), "status": "error"}


def search_products(request, query):
    try:
        # collection.create_index([("name", "text")])
        # results = []
        # cursor = collection.find(
        #     {"$text": {"$search": query}}, {"name": 1, "slug": 1, "_id": 0}
        # ).limit(6)
        # for document in cursor:
        #     results.append(document)
        # return {"data": results, "status": "success"}

        pipeline = [
            {
                "$search": {
                    "index": "default",
                    "autocomplete": {
                        "query": query,
                        "path": "name",
                    },
                }
            },
            {
                "$addFields": {
                    "imageUrl": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/",
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
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "name": 1,
                    "product_sku": 1,
                    "slug": 1,
                    "imageUrl": 1,
                    "imageUrl300": 1,
                    "main_price": 1,
                    "sale_price": 1,
                }
            },
            {"$limit": 5},
        ]

        results = list(collection.aggregate(pipeline))
        return {"data": results, "status": "success"}
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


def get_product_by_slug(request, product_slug):
    try:
        pipeline = [
            {"$match": {"slug": product_slug}},
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


def get_product_details_by_id(product_id):
    try:
        result = list(
            collection.find({"_id": ObjectId(product_id), "deleted_at": None})
        )
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_product_count_by_category_id(category_id):
    try:
        count = collection.count_documents(
            {"category_id": category_id, "deleted_at": None}
        )
        return {"count": count, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def update(id, data):
    try:
        data = dict(data)
        if data["images"] == None:
            del data["images"]
        if data["cover_image"] == None:
            del data["cover_image"]

        print(data)
        result = collection.update_one({"_id": ObjectId(id)}, {"$set": data})
        if result.modified_count == 1:
            return {"message": "data updated successfully", "status": "success"}
        else:
            return {"message": "failed to update", "status": "error"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def update_nested_items(newData, oldData):
    for d1, d2 in zip(newData, oldData):
        # Update current level
        d2["quantity"] += d1["quantity"]
        d2["price"] = d1["price"]

        # Check and update undervarient recursively
        if d1["undervarient"] and d2["undervarient"]:
            update_nested_items(d1["undervarient"], d2["undervarient"])
        elif d1["undervarient"]:
            d2["undervarient"] = d1["undervarient"]

    return oldData


def calculate_parent_quantity(data):
    total_quantity = 0
    for item in data:
        total_quantity += item["quantity"]
    return total_quantity


def update_product_variant(product_id, VariantItem):
    try:
        dict_data = [item.dict() for item in VariantItem]
        data = collection.find_one({"_id": ObjectId(product_id), "deleted_at": None})
        updated_variant = update_nested_items(dict_data, data["variant"])
        total_quantity = calculate_parent_quantity(updated_variant)
        result = collection.update_one(
            {"_id": ObjectId(product_id)},
            {"$set": {"variant": updated_variant, "quantity": total_quantity}},
        )
        if result.modified_count == 1:
            return {"message": "Variant updated successfully", "status": "success"}
        else:
            return {"message": "failed to updated variant", "status": "error"}

    except Exception as e:
        return {"message": str(e), "status": "error"}


def update_only_product_quantity(product_id, total_quantity):
    try:
        result = collection.update_one(
            {"_id": ObjectId(product_id)}, {"$inc": {"quantity": +total_quantity}}
        )
        if result.modified_count == 1:
            return {"message": "Quantity updated successfully", "status": "success"}
        else:
            return {"message": "failed to updated quantity", "status": "error"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def delete_product(product_id: str):
    result = collection.update_one(
        {"_id": ObjectId(product_id)},
        {"$set": {"deleted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}},
    )
    if result.modified_count == 1:
        return {"message": "data deleted successfully", "status": "success"}
    else:
        return {"message": "failed to delete", "status": "error"}


async def create_review(product_id, point, review, review_image, token):
    try:
        data = db["review"].find_one(
            {
                "customer_id": str(token["_id"]),
                "product_id": product_id,
                "deleted_at": None,
            }
        )

        if data == None:
            product_details = collection.find_one(
                {"_id": ObjectId(product_id), "deleted_at": None}
            )

            if product_details == None:
                return {"message": "Product not found", "status": "error"}

            PATH_FILES = getcwd() + "/uploads/review/"
            os.makedirs(PATH_FILES, exist_ok=True)
            filename = f"{uuid.uuid1()}-{os.path.splitext(review_image.filename)[0]}"
            mainFileName = filename + os.path.splitext(review_image.filename)[1]

            with open(PATH_FILES + mainFileName, "wb") as myfile:
                content = await review_image.read()
                myfile.write(content)
                myfile.close()
            resize_image(filename, mainFileName, PATH_FILES)

            # category_data.image = filename + ".webp"

            review_data = {
                "customer_id": str(token["_id"]),
                "product_id": product_id,
                "point": point,
                "review": review,
                "image": filename + ".webp",
                "status": 1,
                "deleted_at": None,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "created_date": str(datetime.now().strftime("%Y-%m-%d")),
                "created_time": str(datetime.now().strftime("%H:%M:%S")),
                "created_by": None,
                "updated_at": None,
                "updated_by": None,
            }

            result = db["review"].insert_one(review_data)
            return {
                "message": "Review Updated",
                "_id": str(result.inserted_id),
                "status": "success",
            }
        else:
            return {
                "message": "review already exist for this product",
                "status": "error",
            }
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_product_wise_review(product_id):
    try:

        pipeline = [
            {"$match": {"status": 1, "product_id": product_id}},
            {
                "$group": {
                    "_id": "$product_id",
                    "total_reviews": {"$sum": 1},
                    "total_points": {"$sum": "$point"},
                    "point_counts": {"$push": "$point"},
                }
            },
            {
                "$project": {
                    "total_reviews": 1,
                    "total_points": 1,
                    "total_count_times_five": {"$multiply": ["$total_reviews", 5]},
                    "point_counts": {
                        "$let": {
                            "vars": {"points": [1, 2, 3, 4, 5]},
                            "in": {
                                "$arrayToObject": {
                                    "$map": {
                                        "input": "$$points",
                                        "as": "point",
                                        "in": {
                                            "k": {"$toString": "$$point"},
                                            "v": {
                                                "$size": {
                                                    "$filter": {
                                                        "input": "$point_counts",
                                                        "as": "p",
                                                        "cond": {
                                                            "$eq": ["$$p", "$$point"]
                                                        },
                                                    }
                                                }
                                            },
                                        },
                                    }
                                }
                            },
                        }
                    },
                }
            },
        ]
        result = list(db["review"].aggregate(pipeline))
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_product_review(request, product_id):
    try:

        pipeline = [
            {"$match": {"status": 1, "product_id": product_id}},
            {"$addFields": {"customer_id_obj": {"$toObjectId": "$customer_id"}}},
            {
                "$lookup": {
                    "from": "user",
                    "localField": "customer_id_obj",
                    "foreignField": "_id",
                    "as": "customer_details",
                }
            },
            {
                "$addFields": {
                    "imageUrl": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/review/",
                            "$image",
                        ]
                    },
                    "imageUrl300": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/review/300/",
                            "$image",
                        ]
                    },
                }
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "customer_id": 1,
                    "product_id": {"$toString": "$product_id"},
                    "point": 1,
                    "review": 1,
                    "image": 1,
                    "imageUrl": 1,
                    "imageUrl300": 1,
                    "status": 1,
                    "order_tracking_id": 1,
                    "status": 1,
                    "customer_details.name": 1,
                    "customer_details.email": 1,
                    "created_at": 1,
                }
            },
        ]
        result = list(db["review"].aggregate(pipeline))
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_products_wise_reviews(request, page, show_page):
    try:
        pipeline = [
            {"$match": {"status": 1, "deleted_at": None}},
            {"$addFields": {"customer_id_obj": {"$toObjectId": "$customer_id"}}},
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
                    "imageUrl": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/",
                            "$product_details.cover_image",
                        ]
                    },
                    "imageUrl100": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/100/",
                            "$product_details.cover_image",
                        ]
                    },
                }
            },
            {
                "$lookup": {
                    "from": "user",
                    "localField": "customer_id_obj",
                    "foreignField": "_id",
                    "as": "customer_details",
                }
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "customer_id": 1,
                    "product_id": 1,
                    "point": 1,
                    "review": 1,
                    "image": 1,
                    "status": 1,
                    "order_tracking_id": 1,
                    "status": 1,
                    "customer_details.name": 1,
                    "customer_details.email": 1,
                    "product_details_name": "$product_details.name",
                    "imageUrl": 1,
                    "imageUrl100": 1,
                    "created_at": 1,
                }
            },
            {
                "$group": {
                    "_id": "$product_id",
                    "grouped_data": {"$push": "$$ROOT"},
                    "product_name": {"$first": "$product_details_name"},
                    "product_imageUrl": {"$first": "$imageUrl"},
                    "product_imageUrl100": {"$first": "$imageUrl100"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "id": "$_id",
                    "product_name": 1,
                    "product_imageUrl": 1,
                    "product_imageUrl100": 1,
                    "grouped_data": 1,
                }
            },
        ]
        documents = paginate(db["review"], pipeline, page, show_page)
        return {"data": documents, "status": "success"}

        # result = list(db["review"].aggregate(pipeline))
        # return {"data": result, "status": "success"}

    except Exception as e:
        return {"message": str(e), "status": "error"}
