from db import db


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
