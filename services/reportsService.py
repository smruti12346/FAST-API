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
        # order_placed_count = db["order"].count_documents(
        #     {
        #         "$and": [
        #             {"status": 1},
        #             {"created_date": {"$gte": start_date, "$lte": end_date}},
        #         ]
        #     }
        # )

        # order_shipped = db["order"].count_documents(
        #     {
        #         "$and": [
        #             {"status": 5},
        #             {"created_date": {"$gte": start_date, "$lte": end_date}},
        #         ]
        #     }
        # )

        # return_request_count = db["order"].count_documents(
        #     {
        #         "$and": [
        #             {"status": 7},
        #             {"created_date": {"$gte": start_date, "$lte": end_date}},
        #         ]
        #     }
        # )
        # total_order_count = db["order"].count_documents(
        #     {
        #         "$and": [
        #             {"status": {"$in": [1, 5, 6]}},
        #             {"created_date": {"$gte": start_date, "$lte": end_date}},
        #         ]
        #     }
        # )
        # Aggregation pipeline for user and order stats
        pipeline = [
            {
                "$match": {
                    "order_details.order_date": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$facet": {
                    "user_stats": [
                        {
                            "$match": {
                                "user_type": {"$ne": 1},
                                "deleted_at": None
                            }
                        },
                        {"$group": {"_id": None, "user_count": {"$sum": 1}}}
                    ],
                    "order_stats": [
                        {
                            "$group": {
                                "_id": "$status",
                                "count": {"$sum": 1},
                                "total_price_sum": {"$sum": "$order_details.total_price"}
                            }
                        }
                    ]
                }
            }
        ]

        # Execute the aggregation pipeline
        result = list(db["order"].aggregate(pipeline))

        # Process the results
        user_count = result[0]["user_stats"][0]["user_count"] if result[0]["user_stats"] else 0
        order_stats = {stat["_id"]: stat for stat in result[0]["order_stats"]}

        # Prepare the output
        output = {
            "data": {
                "user_count": user_count,
                "order_placed_count": round(order_stats.get(1, {}).get("count", 0), 2),
                "order_placed_price_sum": round(order_stats.get(1, {}).get("total_price_sum", 0), 2),
                "order_shipped_count": round(order_stats.get(5, {}).get("count", 0), 2),
                "order_shipped_price_sum": round(order_stats.get(5, {}).get("total_price_sum", 0), 2),
                "return_request_count": round(order_stats.get(7, {}).get("count", 0), 2),
                "return_request_price_sum": round(order_stats.get(7, {}).get("total_price_sum", 0), 2),
                "total_order_count": round(sum(stat["count"] for stat in order_stats.values()), 2),
                "total_order_price_sum": round(sum(stat["total_price_sum"] for stat in order_stats.values()), 2)
            },
            "status": "success"
        }
        # print(output)
        return output
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_data_using_start_date_end_date(start_date, end_date):
    try:
        pipeline = [
            {"$match": {"order_details.order_date": {"$gte": start_date, "$lte": end_date}}},
            {"$group": {"_id": "$order_details.order_date", "count": {"$sum": 1}}},
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
