from db import db
from fastapi import Request
from bson import ObjectId
from datetime import datetime
from .common import paginate
import requests
from requests.auth import HTTPBasicAuth

collection = db["payment"]

PAYPAL_CLIENT_ID = (
    "AU1cUxCKw_DqAP56TgjBD5NSECON9JGBLeKQgm5eVZXqC7xOCZ3tBe1v_A795j9nILSURTfCgTDdmI-9"
)
PAYPAL_SECRET = (
    "EOgzoHLwc5ax-5ytU2ACsRnGmYquyDwslQsPCKHefMtvEDjNSDMmMPW4mIt8gM5A6l1cDiNMNGA5rAIe"
)
PAYPAL_BASE_URL = "https://api-m.sandbox.paypal.com"


def create(data):
    try:
        data = dict(data)
        if (
            collection.count_documents({"api_key": data["api_key"], "deleted_at": None})
            != 0
        ):
            return {"message": "API key already exist", "status": "error"}

        data["id"] = (
            int(dict(collection.find_one({}, sort=[("id", -1)]))["id"]) + 1
            if collection.find_one({}, sort=[("id", -1)]) is not None
            else 1
        )

        result = collection.insert_one(data)
        return {
            "message": "data inserted successfully",
            "_id": str(result.inserted_id),
            "status": "success",
        }
    except Exception as e:
        return {"message": str(e), "status": "error"}


def view(request, page, show_page):
    try:
        pipeline = [
            {"$match": {"deleted_at": None}},
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "id": 1,
                    "name": 1,
                    "getway_name": 1,
                    "currency": 1,
                    "return_url": 1,
                    "cancel_url": 1,
                    "user_id": 1,
                    "password": 1,
                    "api_key": 1,
                    "status": 1,
                    "created_at": 1,
                }
            },
        ]
        result = paginate(collection, pipeline, page, show_page)

        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def view_by_id(id):
    try:
        result = list(collection.find({"_id": ObjectId(id), "deleted_at": None}))
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def view_by_status(status):
    try:
        result = list(collection.find({"status": status, "deleted_at": None}))
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def view_by_getway_name(getway_name):
    try:
        result = list(
            collection.find(
                {"getway_name": getway_name, "status": 1, "deleted_at": None}
            )
        )
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
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


def delete(payment_id: str):
    result = collection.update_one(
        {"_id": ObjectId(payment_id)},
        {"$set": {"deleted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}},
    )
    if result.modified_count == 1:
        return {"message": "data deleted successfully", "status": "success"}
    else:
        return {"message": "failed to delete", "status": "error"}


def change_status(payment_id: str):
    getStatus = view_by_id(payment_id)["data"][0]["status"]

    if getStatus == 0:
        collection.update_many({}, {"$set": {"status": 0}})
        status = 1
    else:
        status = 0

    result = collection.update_one(
        {"_id": ObjectId(payment_id)},
        {"$set": {"status": status}},
    )
    if result.modified_count == 1:
        return {"message": "status changed successfully", "status": "success"}
    else:
        return {"message": "failed to change status", "status": "error"}


def get_paypal_access_token(PAYPAL_CLIENT_ID, PAYPAL_SECRET):
    url = f"{PAYPAL_BASE_URL}/v1/oauth2/token"
    headers = {
        "Accept": "application/json",
        "Accept-Language": "en_US",
    }
    data = {"grant_type": "client_credentials"}
    response = requests.post(
        url,
        headers=headers,
        data=data,
        auth=HTTPBasicAuth(PAYPAL_CLIENT_ID, PAYPAL_SECRET),
    )
    response_data = response.json()
    return response_data["access_token"]


def create_paypal_order(purchase_units, client_id, secret_key, return_url, cancel_url):
    try:
        access_token = get_paypal_access_token(client_id, secret_key)
        url = f"{PAYPAL_BASE_URL}/v2/checkout/orders"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        order_data = {
            "intent": "CAPTURE",
            # "purchase_units": [
            #     {
            #         "reference_id": "d9f80740-38f0-11e8-b467-0ed5f89f718b",
            #         "amount": {"currency_code": "USD", "value": "100.00"},
            #     }
            # ],
            "purchase_units": purchase_units,
            "application_context": {
                "return_url": return_url,
                "cancel_url": cancel_url,
            },
        }
        response = requests.post(url, headers=headers, json=order_data)
        return {"response": response.json(), "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def capture_paypal_order(order_id, client_id, secret_key):
    try:
        access_token = get_paypal_access_token(client_id, secret_key)
        url = f"{PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}/capture"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        response = requests.post(url, headers=headers)
        return {"response": response.json(), "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_paypal_order_details(order_id, client_id, secret_key):
    access_token = get_paypal_access_token(client_id, secret_key)
    url = f"{PAYPAL_BASE_URL}/v2/checkout/orders/{order_id}"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {access_token}",
    }
    response = requests.get(url, headers=headers)
    return response.json()


def get_paypal_capture_id(order_details, reference_id):
    for unit in order_details["purchase_units"]:
        if unit["reference_id"] == reference_id:
            captures = unit.get("payments", {}).get("captures", [])
            if captures:
                return captures[0]["id"]
    return None


def refund_paypal_payment(order_id, reference_id, client_id, secret_key):
    try:
        access_token = get_paypal_access_token(client_id, secret_key)
        order_details = get_paypal_order_details(order_id, client_id, secret_key)
        ref_id = get_paypal_capture_id(order_details, reference_id)
        url = f"{PAYPAL_BASE_URL}/v2/payments/captures/{ref_id}/refund"
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {access_token}",
        }
        # data = {"amount": {"value": "47.34", "currency_code": "USD"}}
        response = requests.post(url, headers=headers, json={}).json()
        status = "success" if "id" in response else "error"
        return {"response": response, "status": status}
    except Exception as e:
        return {"message": str(e), "status": "error"}
