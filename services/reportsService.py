from db import db
from datetime import datetime


def user_pending_and_placed_order_return_request_count(start_date, end_date):
    try:
        user_count = db["user"].count_documents(
            {
                "$and": [
                    {"user_type": {"$ne": 1}},
                    {"deleted_at": None},
                    {"created_date": {"$gte": start_date, "$lte": end_date}},
                ]
            }
        )

        pending_order_count = db["order"].count_documents(
            {
                "$and": [
                    {"status": 1},
                    {"created_date": {"$gte": start_date, "$lte": end_date}},
                ]
            }
        )

        placed_order_count = db["order"].count_documents(
            {
                "$and": [
                    {"status": 5},
                    {"created_date": {"$gte": start_date, "$lte": end_date}},
                ]
            }
        )

        return_request_count = db["order"].count_documents(
            {
                "$and": [
                    {"status": 7},
                    {"created_date": {"$gte": start_date, "$lte": end_date}},
                ]
            }
        )
        return {
            "data": {
                "user_count": user_count,
                "pending_order_count": pending_order_count,
                "placed_order_count": placed_order_count,
                "return_request_count": return_request_count,
            },
            "status": "success",
        }
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_data_using_start_date_end_date(start_date, end_date):
    try:
        pipeline = [
            {"$match": {"created_date": {"$gte": start_date, "$lte": end_date}}},
            {"$group": {"_id": "$created_date", "count": {"$sum": 1}}},
            {"$sort": {"_id": 1}},
        ]
        results = list(db["order"].aggregate(pipeline))
        return {"data": results, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def top_selling_products(request, start_date, end_date):
    try:
        pipeline = [
            # {"$match": {"created_date": {"$gte": start_date, "$lte": end_date}}},
            {"$sort": {"sold_quantity": -1}},
            {
                "$lookup": {
                    "from": "category",
                    "localField": "category_id",
                    "foreignField": "id",
                    "as": "category_details",
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
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "name": 1,
                    "slug": 1,
                    "imageUrl": 1,
                    "imageUrl100": 1,
                    "imageUrl300": 1,
                    "sold_quantity": 1,
                    "category_details.name": 1,
                    "created_at": 1,
                }
            },
            {"$limit": 5},
        ]
        results = list(db["product"].aggregate(pipeline))
        return {"data": results, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}
