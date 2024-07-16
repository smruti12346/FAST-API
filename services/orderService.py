from db import db
from datetime import datetime
from bson import ObjectId
from .common import paginate
from services.smtpService import send_email

collection = db["order"]
from .userService import get_address_by_id, get_bank_details_by_id


def update_variant_quantity(product, variant_arr, total_quantity):
    current_variants = product["variant"]

    variant_names = []

    if len(current_variants) != 0 or len(variant_arr) != 0:
        # Traverse the variant structure to find the specified variant path
        for variant_index in variant_arr:
            if variant_index >= len(current_variants):
                return {"message": "Variant not found.", "status": "error"}

            current_variant = current_variants[variant_index]
            variant_names.append(current_variant["varient"])
            current_variants = current_variant.get("undervarient", [])

        # The final variant in the path
        final_variant = current_variant

        # Check if the final variant has enough quantity
        if final_variant["quantity"] < total_quantity:
            return {
                "message": f"Insufficient quantity for variant {final_variant['varient']}. Required: {total_quantity}, Available: {final_variant['quantity']}",
                "status": "error",
            }

        # Update quantities along the variant path
        current_variants = product["variant"]
        for i, variant_index in enumerate(variant_arr):
            current_variant = current_variants[variant_index]
            current_variant["quantity"] -= total_quantity
            current_variants = current_variant.get("undervarient", [])

    product["quantity"] -= total_quantity
    return {"data": product, "status": "success"}


def check_order_quantity(product_id, varientArr):
    try:
        result = list(
            db["product"].find({"_id": ObjectId(product_id), "deleted_at": None})
        )
        updated_product = update_variant_quantity(result[0], varientArr, 2)
        print(updated_product)
        # return updated_product
    except Exception as e:
        return {"message": str(e), "status": "error"}


def check_order_quantity_by_order(product_details):
    try:
        if len(product_details) == 0:
            return {"message": "please choose product", "status": "error"}
        for existing_order in product_details:
            existing_order_data = existing_order.dict()
            result = list(
                db["product"].find(
                    {
                        "_id": ObjectId(existing_order_data["product_id"]),
                        "deleted_at": None,
                    }
                )
            )
            updated_product = update_variant_quantity(
                result[0],
                existing_order_data["order_details"]["varientArr"],
                existing_order_data["order_details"]["total_quantity"],
            )

            if updated_product["status"] == "error":
                return updated_product

        return {"message": "Product available", "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def order_placed(customer_id, product_details):
    try:
        orders = []
        productQuntityArrs = []

        if len(product_details) == 0:
            return {"message": "please choose product", "status": "error"}

        for existing_order in product_details:
            data = existing_order.dict()
            data["customer_id"] = customer_id
            address = get_address_by_id(data["customer_id"])
            if address["status"] == "success":
                primary_status_items = (
                    [
                        item
                        for item in address["data"]
                        if item["primary_status"] == 1
                        and item.get("deleted_at") is None
                        and item["status"] == 1
                    ]
                    if address.get("data")
                    else []
                )
                if len(primary_status_items) == 0:
                    return {"message": "Please enter your address", "status": "error"}

                data["address"] = primary_status_items[0]

            data["bank_details"] = []
            data["order_tracking_id"] = 1
            data["status"] = 0
            data["deleted_at"] = None
            data["created_by"] = data["customer_id"]
            data["updated_by"] = None
            data["created_at"] = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            data["created_date"] = str(datetime.now().strftime("%Y-%m-%d"))
            data["created_time"] = str(datetime.now().strftime("%H:%M:%S"))
            data["updated_at"] = None

            data["order_details"]["order_date"] = str(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            data["order_details"]["order_cancel_status"] = None
            data["order_details"]["order_cancel_date"] = None
            data["order_details"]["order_cancel_amount"] = None
            data["order_details"]["shipped_date"] = None
            data["order_details"]["shipped_id"] = None
            data["order_details"]["delivery_date"] = None

            productQuntityArr = {
                "_id": data["product_id"],
                "total_quantity": data["order_details"]["total_quantity"],
            }

            productQuntityArrs.append(productQuntityArr)
            orders.append(data)

        # insert data before check quantity with status 0
        resultInserted = collection.insert_many(orders)

        # check quantity
        for existing_order in product_details:
            existing_order_data = existing_order.dict()
            result = list(
                db["product"].find(
                    {
                        "_id": ObjectId(existing_order_data["product_id"]),
                        "deleted_at": None,
                    }
                )
            )
            updated_product = update_variant_quantity(
                result[0],
                existing_order_data["order_details"]["varientArr"],
                existing_order_data["order_details"]["total_quantity"],
            )

            if updated_product["status"] == "error":
                return updated_product

        # update quantity and varient after check quantity
        for existing_order in product_details:
            existing_order_data = existing_order.dict()
            result = list(
                db["product"].find(
                    {
                        "_id": ObjectId(existing_order_data["product_id"]),
                        "deleted_at": None,
                    }
                )
            )
            updated_product = update_variant_quantity(
                result[0],
                existing_order_data["order_details"]["varientArr"],
                existing_order_data["order_details"]["total_quantity"],
            )

            db["product"].update_one(
                {"_id": ObjectId(existing_order_data["product_id"])},
                {
                    "$set": {
                        "quantity": int(updated_product["data"]["quantity"]),
                        "variant": updated_product["data"]["variant"],
                    },
                    "$inc": {
                        "sold_quantity": +existing_order_data["order_details"][
                            "total_quantity"
                        ]
                    },
                },
            )

        # insert data after check quantity with status 1
        filter = {"_id": {"$in": resultInserted.inserted_ids}}
        update = {"$set": {"status": 1}}
        collection.update_many(filter, update)

        return {"message": "Order placed successfully", "status": "success"}

    except Exception as e:
        return {"message": str(e), "status": "error"}


def check_quantity(document):
    try:
        db_document = db["product"].find_one({"_id": ObjectId(document["_id"])})
        if db_document:
            return db_document["quantity"] >= document["total_quantity"]
        else:
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def update_quantity(document):
    try:
        db["product"].update_one(
            {"_id": ObjectId(document["_id"])},
            {
                "$inc": {
                    "quantity": -document["total_quantity"],
                    "sold_quantity": +document["total_quantity"],
                }
            },
        )
    except Exception as e:
        print(f"An error occurred: {e}")


def get_orders(request):
    try:
        pipeline = [
            {"$match": {}},
            {"$addFields": {"product_id_obj": {"$toObjectId": "$product_id"}}},
            {"$addFields": {"customer_id_obj": {"$toObjectId": "$customer_id"}}},
            {
                "$lookup": {
                    "from": "product",
                    "localField": "product_id_obj",
                    "foreignField": "_id",
                    "as": "product_details",
                }
            },
            {
                "$lookup": {
                    "from": "category",
                    "localField": "product_details.category_id",
                    "foreignField": "id",
                    "as": "category_details",
                }
            },
            {
                "$lookup": {
                    "from": "category",
                    "localField": "category_details.parent_id_arr",
                    "foreignField": "id",
                    "as": "parent_docs",
                }
            },
            {
                "$lookup": {
                    "from": "location",
                    "localField": "address.country_id",
                    "foreignField": "id",
                    "as": "parent_docs",
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
            {"$unwind": "$product_details"},
            {"$unwind": "$category_details"},
            {"$unwind": "$customer_details"},
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
                    "product_details.name": "$product_details.name",
                    "product_details.cover_image": "$product_details.cover_image",
                    "product_details.category_id": "$product_details.category_id",
                    "category_details.name": "$category_details.name",
                    "category_details.parent_id_arr": "$category_details.parent_id_arr",
                    "category_details.parent_arr": "$parent_docs.name",
                    "customer_details.name": "$customer_details.name",
                    "customer_details.email": "$customer_details.email",
                }
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "customer_id": 1,
                    "product_id": {"$toString": "$product_id"},
                    "order_details": 1,
                    "payment_details": 1,
                    "address": 1,
                    "bank_details": 1,
                    "order_tracking_id": 1,
                    "status": 1,
                    "product_details._id": {"$toString": "$product_details._id"},
                    "product_details.name": 1,
                    "product_details.cover_image": 1,
                    "product_details.imageUrl": 1,
                    "product_details.imageUrl100": 1,
                    "product_details.imageUrl300": 1,
                    "product_details.category_id": 1,
                    "category_details.name": 1,
                    "category_details.parent_arr": 1,
                    "customer_details.name": 1,
                    "customer_details.email": 1,
                }
            },
        ]
        result = list(collection.aggregate(pipeline))
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_all_orders(request, page, show_page):
    try:
        pipeline = [
            {"$match": {}},
            {"$addFields": {"product_id_obj": {"$toObjectId": "$product_id"}}},
            {"$addFields": {"customer_id_obj": {"$toObjectId": "$customer_id"}}},
            {
                "$lookup": {
                    "from": "product",
                    "localField": "product_id_obj",
                    "foreignField": "_id",
                    "as": "product_details",
                }
            },
            {
                "$lookup": {
                    "from": "category",
                    "localField": "product_details.category_id",
                    "foreignField": "id",
                    "as": "category_details",
                }
            },
            {
                "$lookup": {
                    "from": "category",
                    "localField": "category_details.parent_id_arr",
                    "foreignField": "id",
                    "as": "parent_docs",
                }
            },
            {
                "$lookup": {
                    "from": "location",
                    "localField": "address.country_id",
                    "foreignField": "id",
                    "as": "parent_docs",
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
            {"$unwind": "$product_details"},
            {"$unwind": "$category_details"},
            {"$unwind": "$customer_details"},
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
                    "product_details.name": "$product_details.name",
                    "product_details.cover_image": "$product_details.cover_image",
                    "product_details.category_id": "$product_details.category_id",
                    "category_details.name": "$category_details.name",
                    "category_details.parent_id_arr": "$category_details.parent_id_arr",
                    "category_details.parent_arr": "$parent_docs.name",
                    "customer_details.name": "$customer_details.name",
                    "customer_details.email": "$customer_details.email",
                }
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "customer_id": 1,
                    "product_id": {"$toString": "$product_id"},
                    "order_details": 1,
                    "payment_details": 1,
                    "address": 1,
                    "bank_details": 1,
                    "order_tracking_id": 1,
                    "status": 1,
                    "product_details._id": {"$toString": "$product_details._id"},
                    "product_details.name": 1,
                    "product_details.cover_image": 1,
                    "product_details.imageUrl": 1,
                    "product_details.imageUrl100": 1,
                    "product_details.imageUrl300": 1,
                    "product_details.category_id": 1,
                    "category_details.name": 1,
                    "category_details.parent_arr": 1,
                    "customer_details.name": 1,
                    "customer_details.email": 1,
                }
            },
        ]
        
        # result = list(collection.aggregate(pipeline))
        result = paginate(collection, pipeline, page, show_page)
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_orders_by_counts(request, page, show_page):
    try:
        pipeline = [
            {"$match": {}},
            {"$sort": {"created_at": -1}},
            {"$addFields": {"product_id_obj": {"$toObjectId": "$product_id"}}},
            {"$addFields": {"customer_id_obj": {"$toObjectId": "$customer_id"}}},
            {
                "$lookup": {
                    "from": "product",
                    "localField": "product_id_obj",
                    "foreignField": "_id",
                    "as": "product_details",
                }
            },
            {
                "$lookup": {
                    "from": "category",
                    "localField": "product_details.category_id",
                    "foreignField": "id",
                    "as": "category_details",
                }
            },
            {
                "$lookup": {
                    "from": "category",
                    "localField": "category_details.parent_id_arr",
                    "foreignField": "id",
                    "as": "parent_docs",
                }
            },
            {
                "$lookup": {
                    "from": "location",
                    "localField": "address.country_id",
                    "foreignField": "id",
                    "as": "parent_docs",
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
            {"$unwind": "$product_details"},
            {"$unwind": "$category_details"},
            {"$unwind": "$customer_details"},
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
                    "product_details.name": "$product_details.name",
                    "product_details.cover_image": "$product_details.cover_image",
                    "product_details.category_id": "$product_details.category_id",
                    "category_details.name": "$category_details.name",
                    "category_details.parent_id_arr": "$category_details.parent_id_arr",
                    "category_details.parent_arr": "$parent_docs.name",
                    "customer_details.name": "$customer_details.name",
                    "customer_details.email": "$customer_details.email",
                }
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "customer_id": 1,
                    "product_id": {"$toString": "$product_id"},
                    "order_details": 1,
                    "payment_details": 1,
                    "address": 1,
                    "bank_details": 1,
                    "order_tracking_id": 1,
                    "status": 1,
                    "product_details._id": {"$toString": "$product_details._id"},
                    "product_details.name": 1,
                    "product_details.cover_image": 1,
                    "product_details.imageUrl": 1,
                    "product_details.imageUrl100": 1,
                    "product_details.imageUrl300": 1,
                    "product_details.category_id": 1,
                    "category_details.name": 1,
                    "category_details.parent_arr": 1,
                    "customer_details.name": 1,
                    "customer_details.email": 1,
                    "created_at": 1,
                }
            },
        ]

        documents = paginate(collection, pipeline, page, show_page)
        return {"data": documents, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def find_variant(variants, variant_arr):
    current_variants = variants
    final_obj = {}
    variant_arr_name = []

    for variant_index in variant_arr:
        if variant_index >= len(current_variants):
            return None

        current_variant = current_variants[variant_index]
        variant_arr_name.append(current_variant["varient"])
        final_obj = current_variant
        current_variants = current_variant.get("undervarient", [])

    final_obj["VarientArrName"] = variant_arr_name
    return final_obj


def get_all_orders_by_user(request, user_id):
    try:
        pipeline = [
            {"$match": {"customer_id": user_id}},
            {"$addFields": {"product_id_obj": {"$toObjectId": "$product_id"}}},
            {
                "$lookup": {
                    "from": "product",
                    "localField": "product_id_obj",
                    "foreignField": "_id",
                    "as": "product_details",
                }
            },
            {
                "$lookup": {
                    "from": "location",
                    "localField": "address.country_id",
                    "foreignField": "id",
                    "as": "country_details",
                }
            },
            {"$unwind": "$country_details"},
            {"$unwind": "$country_details.states"},
            {
                "$match": {
                    "$expr": {
                        "$eq": ["$country_details.states.id", "$address.state_id"]
                    }
                }
            },
            {"$unwind": "$country_details.states.cities"},
            {
                "$match": {
                    "$expr": {
                        "$eq": ["$country_details.states.cities.id", "$address.city_id"]
                    }
                }
            },
            {"$unwind": "$product_details"},
            {
                "$addFields": {
                    "product_details.imageUrl100": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/100/",
                            "$product_details.cover_image",
                        ]
                    },
                    "product_details.name": "$product_details.name",
                    "product_details.slug": "$product_details.slug",
                    "address.country_name": "$country_details.name",
                    "address.state_name": "$country_details.states.name",
                    "address.city_name": "$country_details.states.cities.name",
                }
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "customer_id": 1,
                    "product_id": {"$toString": "$product_id"},
                    "order_details": 1,
                    "payment_details": 1,
                    "address": 1,
                    "bank_details": 1,
                    "order_tracking_id": 1,
                    "status": 1,
                    "product_details._id": {"$toString": "$product_details._id"},
                    "product_details.name": 1,
                    "product_details.slug": 1,
                    "product_details.imageUrl100": 1,
                    "created_at": 1,
                }
            },
        ]
        result = list(collection.aggregate(pipeline))

        # print(result)
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_all_orders_by_order_id(order_id):
    try:
        pipeline = [
            {"$match": {"_id": ObjectId(order_id)}},
            {"$addFields": {"product_id_obj": {"$toObjectId": "$product_id"}}},
            {"$addFields": {"customer_id_obj": {"$toObjectId": "$customer_id"}}},
            {
                "$lookup": {
                    "from": "product",
                    "localField": "product_id_obj",
                    "foreignField": "_id",
                    "as": "product_details",
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
                    "from": "location",
                    "localField": "address.country_id",
                    "foreignField": "id",
                    "as": "country_details",
                }
            },
            {"$unwind": "$country_details"},
            {"$unwind": "$country_details.states"},
            {
                "$match": {
                    "$expr": {
                        "$eq": ["$country_details.states.id", "$address.state_id"]
                    }
                }
            },
            {"$unwind": "$country_details.states.cities"},
            {
                "$match": {
                    "$expr": {
                        "$eq": ["$country_details.states.cities.id", "$address.city_id"]
                    }
                }
            },
            {"$unwind": "$product_details"},
            {"$unwind": "$user_details"},
            {
                "$addFields": {
                    "product_details.name": "$product_details.name",
                    "product_details.slug": "$product_details.slug",
                    "product_details.main_price": "$product_details.main_price",
                    "product_details.description": "$product_details.description",
                    "address.country_name": "$country_details.name",
                    "address.state_name": "$country_details.states.name",
                    "address.city_name": "$country_details.states.cities.name",
                    "user_details.email": "$user_details.email",
                    "user_details.name": "$user_details.name",
                }
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "customer_id": 1,
                    "product_id": {"$toString": "$product_id"},
                    "order_details": 1,
                    "payment_details": 1,
                    "address": 1,
                    "bank_details": 1,
                    "order_tracking_id": 1,
                    "status": 1,
                    "product_details._id": {"$toString": "$product_details._id"},
                    "product_details.name": 1,
                    "product_details.slug": 1,
                    "product_details.main_price": 1,
                    "product_details.description": 1,
                    "user_details.email": 1,
                    "user_details.name": 1,
                    "created_at": 1,
                }
            },
        ]
        result = list(collection.aggregate(pipeline))

        # print(result)
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def update_payment_status(order_id):
    try:
        result = collection.update_one(
            {"_id": ObjectId(order_id)},
            {
                "$set": {
                    "payment_details.payment_method": "Offline",
                    "payment_details.payment_status": 1,
                    "payment_details.transaction_status": 1,
                    "payment_details.payment_status": 1,
                    "payment_details.payment_date": str(
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ),
                    "payment_details.payment_status_message": "COMPLETED",
                }
            },
        )
        if result.modified_count == 1:
            return {"message": "Payment successfully", "status": "success"}
        else:
            return {"message": "failed to payment", "status": "error"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def update_order_status(order_id, status):
    try:
        result = collection.update_one(
            {"_id": ObjectId(order_id)},
            {"$set": {"status": status}},
        )
        if result.modified_count == 1:
            return {"message": "status updated successfully", "status": "success"}
        else:
            return {"message": "failed update status", "status": "error"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_all_orders_status_wise(request, statusArr):
    try:
        pipeline = [
            {"$match": {"status": {"$in": statusArr}}},
            {"$addFields": {"product_id_obj": {"$toObjectId": "$product_id"}}},
            {"$addFields": {"customer_id_obj": {"$toObjectId": "$customer_id"}}},
            {
                "$lookup": {
                    "from": "product",
                    "localField": "product_id_obj",
                    "foreignField": "_id",
                    "as": "product_details",
                }
            },
            {
                "$lookup": {
                    "from": "category",
                    "localField": "product_details.category_id",
                    "foreignField": "id",
                    "as": "category_details",
                }
            },
            {
                "$lookup": {
                    "from": "category",
                    "localField": "category_details.parent_id_arr",
                    "foreignField": "id",
                    "as": "parent_docs",
                }
            },
            {
                "$lookup": {
                    "from": "location",
                    "localField": "address.country_id",
                    "foreignField": "id",
                    "as": "parent_docs",
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
            {"$unwind": "$product_details"},
            {"$unwind": "$category_details"},
            {"$unwind": "$customer_details"},
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
                    "product_details.name": "$product_details.name",
                    "product_details.cover_image": "$product_details.cover_image",
                    "product_details.category_id": "$product_details.category_id",
                    "category_details.name": "$category_details.name",
                    "category_details.parent_id_arr": "$category_details.parent_id_arr",
                    "category_details.parent_arr": "$parent_docs.name",
                    "customer_details.name": "$customer_details.name",
                    "customer_details.email": "$customer_details.email",
                }
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "customer_id": 1,
                    "product_id": {"$toString": "$product_id"},
                    "order_details": 1,
                    "payment_details": 1,
                    "address": 1,
                    "bank_details": 1,
                    "order_tracking_id": 1,
                    "status": 1,
                    "product_details._id": {"$toString": "$product_details._id"},
                    "product_details.name": 1,
                    "product_details.cover_image": 1,
                    "product_details.imageUrl": 1,
                    "product_details.imageUrl100": 1,
                    "product_details.imageUrl300": 1,
                    "product_details.category_id": 1,
                    "category_details.name": 1,
                    "category_details.parent_arr": 1,
                    "customer_details.name": 1,
                    "customer_details.email": 1,
                    "created_at": 1,
                }
            },
        ]
        result = list(collection.aggregate(pipeline))
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_all_orders_count_status_wise():
    try:
        pipeline = [
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1},
                }
            }
        ]

        result = list(collection.aggregate(pipeline))
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_order_invoice(data, background_tasks):
    try:
        data = dict(data)
        results = get_all_orders_by_order_id(data['order_id'])

        if(results['status'] == "success" and results['data'][0]):
            result = results['data'][0]
            if result['status'] == 3 or result['status'] == 4 or result['status'] == 5 or result['status'] == 6 :
                # print(result)
                body = f"""
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Invoice</title>
                        <style>
                            body {{
                                font-family: 'Arial', sans-serif;
                                margin: 0;
                                padding: 0;
                                background-color: #f5f5f5;
                            }}
                            
                            .invoice-box {{
                                max-width: 800px;
                                margin: 20px auto;
                                padding: 30px;
                                border: 1px solid #eee;
                                background-color: #fff;
                            }}
                            
                            table {{
                                width: 100%;
                                line-height: inherit;
                                text-align: left;
                                border-collapse: collapse;
                            }}
                            
                            table td {{
                                padding: 8px;
                                vertical-align: top;
                            }}
                            
                            table tr.top table td {{
                                padding-bottom: 20px;
                            }}
                            
                            table tr.top table td.title {{
                                font-size: 45px;
                                line-height: 45px;
                                color: #333;
                            }}
                            
                            table tr.information table td {{
                                padding-bottom: 40px;
                            }}
                            
                            table tr.heading td {{
                                background: #eee;
                                border-bottom: 1px solid #ddd;
                                font-weight: bold;
                                text-align: right;
                            }}
                            
                            table tr.item td {{
                                border-bottom: 1px solid #eee;
                                text-align: right;
                            }}
                            
                            table tr.item.last td {{
                                border-bottom: none;
                            }}
                            
                            table tr.total td:nth-child(2) {{
                                border-top: 2px solid #eee;
                                font-weight: bold;
                                padding-top: 10px;
                                padding-bottom: 10px;
                            }}
                            
                            .terms {{
                                margin-top: 40px;
                                font-size: 14px;
                            }}
                            
                            h2, p {{
                                margin: 0;
                            }}
                            
                            h2 {{
                                font-size: 22px;
                            }}
                            
                            .title p {{
                                font-size: 14px;
                                line-height: 1.5;
                            }}
                            
                            .top td, .information td, .heading td, .item td, .total td {{
                                font-size: 14px;
                            }}
                            
                            .left {{
                                float: left;
                                width: 60%;
                            }}
                            
                            .right {{
                                float: right;
                                width: 40%;
                                text-align: right;
                            }}
                            
                            .clearfix {{
                                overflow: auto;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="invoice-box">
                            <table>
                                <tr class="top">
                                    <td colspan="5">
                                        <div class="clearfix">
                                            <div class="left">
                                                <h2>Zylker Electronics Hub</h2>
                                                <p>14B, Northern Street Greater South Avenue<br>
                                                New York New York 10001 U.S.A</p>
                                            </div>
                                            <div class="right">
                                                <p>INVOICE</p>
                                                <p>Invoice# : {result.get('_id', '')}<br>
                                                Order Date : {result.get('created_at', '')}<br>
                                                Terms : Due on Receipt<br>
                                                Due Date : {result.get('created_at', '')}</p>
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                                <tr class="information">
                                    <td colspan="5">
                                        <div class="clearfix">
                                            <div class="left">
                                                <p>Bill To</p>
                                                <p>{result.get('user_details')['name']}<br>
                                                {result.get('address')['country_name']}<br>
                                                {result.get('address')['state_name']}<br>
                                                {result.get('address')['city_name']}, {result.get('address')['pin_number']}</p>
                                            </div>
                                            <div class="right">
                                                <p>Ship To</p>
                                                <p>{result.get('address')['full_name']}<br>
                                                {result.get('address')['country_name']}<br>
                                                {result.get('address')['state_name']}<br>
                                                {result.get('address')['city_name']}, {result.get('address')['pin_number']}, near {result.get('address')['landmark']}</p>
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                                <tr class="heading">
                                    <td>#</td>
                                    <td>Item & Description</td>
                                    <td>Qty</td>
                                    <td>Rate</td>
                                    <td>Amount</td>
                                </tr>
                                <!-- Example of dynamic item list -->
                                
                                <tr class="item">
                                    <td>1</td>
                                    <td>{result.get('product_details')['name']}</td>
                                    <td>{result.get('order_details')['total_quantity']}</td>
                                    <td>{result.get('product_details')['main_price']}</td>
                                    <td>{result.get('order_details')['sale_price']}</td>
                                </tr>
                                <tr class="total">
                                    <td colspan="4" style="text-align: right;">Sub Total</td>
                                    <td style="text-align: right;">{result.get('order_details')['sale_price']}</td>
                                </tr>
                                <tr class="total">
                                    <td colspan="4" style="text-align: right;">Discount</td>
                                    <td style="text-align: right;">{result.get('order_details')['discountAmount']} ( {result.get('order_details')['discountInPercentage']}% )</td>
                                </tr>
                                <tr class="total">
                                    <td colspan="4" style="text-align: right;">Balance Due</td>
                                    <td style="text-align: right;">{result.get('order_details')['total_price']}</td>
                                </tr>
                            </table>
                            <p class="terms">Thanks for shopping with us.</p>
                            <p class="terms">Terms & Conditions<br>
                            Full payment is due upon receipt of this invoice.<br>
                            Late payments may incur additional charges or interest as per the applicable laws.</p>
                        </div>
                    </body>
                    </html>
                    """
                # print(body)
                background_tasks.add_task(send_email, result.get('user_details')['email'], "Invoice Report", body)            
                return {"message": "Email sent successfully", "status": "success"}
            else:
                return {"message": "Unable to generate invoice", "status": "error"}
        else:
            return {"message": "No data found", "status": "error"}
    except Exception as e:
        return {"message": str(e), "status": "error"}
