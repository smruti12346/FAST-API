from db import db
from datetime import datetime


def user_pending_and_placed_order_return_request_count():
    try:
        user_count = db["user"].count_documents(
            {"user_type": {"$ne": 1}, "deleted_at": None}
        )
        pending_order_count = db["order"].count_documents({"status": 1})
        placed_order_count = db["order"].count_documents({"status": 2})
        return_request_count = db["order"].count_documents({"status": 4})

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
