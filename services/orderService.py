from db import db
from datetime import datetime
from bson import ObjectId

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

            # bank_details = get_bank_details_by_id(data["customer_id"])
            # if bank_details["status"] == "success":
            #     primary_status_items = (
            #         [
            #             item
            #             for item in bank_details["data"]
            #             if item["primary_status"] == 1
            #         ]
            #         if bank_details.get("data")
            #         else []
            #     )
            #     if len(primary_status_items) == 0:
            #         return {
            #             "message": "Please enter your bank details",
            #             "status": "error",
            #         }

            #     data["bank_details"] = primary_status_items[0]

            data["bank_details"] = []
            data["order_tracking_id"] = 1
            data["status"] = 1
            data["deleted_at"] = None
            data["created_by"] = data["customer_id"]
            data["updated_by"] = None
            data["created_at"] = str(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
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

        collection.insert_many(orders)
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


def get_all_orders(request):
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
