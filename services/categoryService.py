from db import db
from bson import ObjectId
from datetime import datetime
from fastapi import Request
from .productService import get_product_count_by_category_id
from .common import paginate
import json

collection = db["category"]


def create(data):
    try:
        data = dict(data)

        if collection.count_documents({"slug": data["slug"], "deleted_at": None}) != 0:
            return {"message": "slug already exist", "status": "error"}

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
            doc["imageUrl"] = (
                f"{str(request.base_url)[:-1]}/uploads/category/{doc['image']}"
            )
            doc["imageUrl100"] = (
                f"{str(request.base_url)[:-1]}/uploads/category/100/{doc['image']}.webp"
            )
            doc["imageUrl300"] = (
                f"{str(request.base_url)[:-1]}/uploads/category/300/{doc['image']}.webp"
            )
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


def get_category_by_unique_id(id):
    try:
        result = list(collection.find({"id": id, "deleted_at": None}))
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


def get_all_sub_category(request):
    try:
        pipeline = [{"$match": {"deleted_at": None, "parent_id": 0}}]
        results = list(collection.aggregate(pipeline))
        mainArr = dict()
        for result in results:
            documentOnes = list(collection.find({"parent_id": result["id"]}))
            id = result["id"]
            mainArr[id] = []
            for documentOne in documentOnes:
                idOne = documentOne["id"]
                documentTwos = list(
                    collection.find({"parent_id_arr": {"$elemMatch": {"$eq": idOne}}})
                )
                if len(documentTwos) == 0:
                    mainArr[id].append(idOne)
                mainArr[idOne] = []
                for documentTwo in documentTwos:
                    if (
                        len(list(collection.find({"parent_id": documentTwo["id"]})))
                        == 0
                    ):
                        idTwo = documentTwo["id"]
                        mainArr[idOne].append(idTwo)
        filteredMainArr = {k: v for k, v in mainArr.items() if v}
        # print(filteredMainArr)

        mainArr = []
        for docOne in filteredMainArr:
            data = get_category_by_unique_id(docOne)
            mainObj = dict()
            if data["data"] and len(data["data"]) > 0:
                mainObj["name"] = data["data"][0]["name"]
                mainObj["id"] = docOne

            mainObj["subcategory"] = []
            for docTwo in filteredMainArr[docOne]:
                # print(docTwo)
                dataTwo = get_category_by_unique_id(docTwo)
                mainObjTwo = dict()
                if dataTwo["data"] and len(dataTwo["data"]) > 0:
                    mainObjTwo["name"] = dataTwo["data"][0]["name"]
                    mainObjTwo["id"] = docTwo
                    mainObjTwo["count"] = get_product_count_by_category_id(docTwo)[
                        "count"
                    ]
                mainObj["subcategory"].append(mainObjTwo)
            mainArr.append(mainObj)

        # print(mainArr)
        return {"data": mainArr, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_category_wise_product(
    request, page, identifier, show_page, sort_by, price_range, is_slug=True
):
    try:

        price_range = json.loads(price_range) if price_range is not None else None

        if is_slug:
            category_details = list(
                collection.find({"slug": identifier, "deleted_at": None})
            )

            if len(category_details) > 0:
                category_id = category_details[0]["id"]
            else:
                return {"message": "category name not exist", "status": "error"}
        else:
            category_id = int(identifier)

        pipeline = [
            {"$match": {"parent_id_arr": category_id}},
            {
                "$lookup": {
                    "from": "category",
                    "localField": "id",
                    "foreignField": "parent_id",
                    "as": "children",
                }
            },
            {"$match": {"children": {"$size": 0}}},
            {"$project": {"id": 1}},
        ]

        result = list(collection.aggregate(pipeline))

        mainArr = [doc["id"] for doc in result] if result else [category_id]

        query = [
            {"$match": {"category_id": {"$in": mainArr}}},
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
                    "_id": {"$toString": "$_id"},
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

        if price_range is not None:
            query.append(
                {
                    "$match": {
                        "sale_price": {
                            "$gte": int(price_range[0]),
                            "$lte": int(price_range[1]),
                        },
                    }
                }
            )

        if sort_by == "date":
            query.append({"$sort": {"created_at": -1}})
        elif sort_by == "high_selling":
            query.append({"$sort": {"sold_quantity": -1}})
        elif sort_by == "sort_asc":
            query.append({"$sort": {"name": -1}})

        documents = paginate(db["product"], query, page, show_page)
        query = [
            stage
            for stage in query
            if "$match" not in stage or "sale_price" not in stage["$match"]
        ]
        query.append(
            {
                "$group": {
                    "_id": None,
                    "max_price": {"$max": "$sale_price"},
                    "min_price": {"$min": "$sale_price"},
                }
            }
        )

        price = list(db["product"].aggregate(query))
        max_price = price[0]["max_price"]
        min_price = price[0]["min_price"]

        documents["max_price"] = max_price
        documents["min_price"] = min_price

        return {"data": documents, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


# def get_category_id_wise_product(
#     request, page, category_id, show_page, sort_by, price_range
# ):
#     try:
#         price_range = json.loads(price_range) if price_range is not None else None
#         print(price_range)
#         pipeline = [
#             {"$match": {"parent_id_arr": category_id}},
#             {
#                 "$lookup": {
#                     "from": "category",
#                     "localField": "id",
#                     "foreignField": "parent_id",
#                     "as": "children",
#                 }
#             },
#             {"$match": {"children": {"$size": 0}}},
#             {"$project": {"id": 1}},
#         ]

#         result = list(collection.aggregate(pipeline))
#         mainArr = [doc["id"] for doc in result]

#         query = [
#             {"$match": {"category_id": {"$in": mainArr}}},
#             {
#                 "$lookup": {
#                     "from": "category",
#                     "localField": "category_id",
#                     "foreignField": "id",
#                     "as": "category",
#                 }
#             },
#             {
#                 "$addFields": {
#                     "category": {"$arrayElemAt": ["$category", 0]},
#                     "_id": {"$toString": "$_id"},
#                 }
#             },
#             {
#                 "$addFields": {
#                     "_id": {"$toString": "$_id"},
#                     "category_parent_id_arr": "$category.parent_id_arr",
#                     "imageUrl": {
#                         "$concat": [
#                             str(request.base_url)[:-1],
#                             "/uploads/products/",
#                             "$cover_image",
#                         ]
#                     },
#                     "imageUrl100": {
#                         "$concat": [
#                             str(request.base_url)[:-1],
#                             "/uploads/products/100/",
#                             "$cover_image",
#                         ]
#                     },
#                     "imageUrl300": {
#                         "$concat": [
#                             str(request.base_url)[:-1],
#                             "/uploads/products/300/",
#                             "$cover_image",
#                         ]
#                     },
#                 }
#             },
#             {"$unset": "category"},
#             {
#                 "$lookup": {
#                     "from": "category",
#                     "localField": "category_parent_id_arr",
#                     "foreignField": "id",
#                     "as": "parent_categories",
#                 }
#             },
#             {"$addFields": {"parent_category_names": "$parent_categories.name"}},
#             {"$unset": "parent_categories"},
#         ]

#         if price_range is not None:
#             query.append(
#                 {
#                     "$match": {
#                         "sale_price": {
#                             "$gte": int(price_range[0]),
#                             "$lte": int(price_range[1]),
#                         },
#                     }
#                 }
#             )

#         if sort_by == "date":
#             query.append({"$sort": {"created_at": -1}})
#         elif sort_by == "high_selling":
#             query.append({"$sort": {"sold_quantity": -1}})
#         elif sort_by == "sort_asc":
#             query.append({"$sort": {"name": -1}})

#         # print(query)
#         documents = paginate(db["product"], query, page, show_page)
#         query = [
#             stage
#             for stage in query
#             if "$match" not in stage or "sale_price" not in stage["$match"]
#         ]
#         query.append(
#             {
#                 "$group": {
#                     "_id": None,
#                     "max_price": {"$max": "$sale_price"},
#                     "min_price": {"$min": "$sale_price"},
#                 }
#             }
#         )

#         price = list(db["product"].aggregate(query))
#         max_price = price[0]["max_price"]
#         min_price = price[0]["min_price"]

#         documents["max_price"] = max_price
#         documents["min_price"] = min_price

#         return {"data": documents, "status": "success"}
#     except Exception as e:
#         return {"message": str(e), "status": "error"}
