import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pydantic import EmailStr
from typing import List
from db import db
from bson import ObjectId
from datetime import datetime
from .common import paginate

collection = db["smtp"]


def create(data, id):
    try:
        data = dict(data)
        # if collection.count_documents({"deleted_at": None}) != 0:
        #     return {"message": "You can add only one tax details", "status": "error"}
        data["created_by"] = id
        result = collection.insert_one(data)
        return {
            "message": "data inserted successfully",
            "_id": str(result.inserted_id),
            "status": "success",
        }
    except Exception as e:
        return {"message": str(e), "status": "error"}


def view(page, show_page):
    try:
        pipeline = [
            {"$match": {"deleted_at": None}},
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "name": 1,
                    "smtp_server": 1,
                    "smtp_port": 1,
                    "smtp_username": 1,
                    "smtp_password": 1,
                    "status": 1,
                    "created_at": 1,
                }
            },
        ]
        result = paginate(collection, pipeline, page, show_page)
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def view_by_status(status):
    try:
        pipeline = [
            {"$match": {"status": status, "deleted_at": None}},
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "name": 1,
                    "smtp_server": 1,
                    "smtp_port": 1,
                    "smtp_username": 1,
                    "smtp_password": 1,
                    "status": 1,
                    "created_at": 1,
                }
            },
        ]
        result = collection.aggregate(pipeline)
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
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


def viewTax():
    try:
        pipeline = [
            {"$match": {"deleted_at": None}},
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "name": 1,
                    "smtp_server": 1,
                    "smtp_port": 1,
                    "smtp_username": 1,
                    "smtp_password": 1,
                    "status": 1,
                    "created_at": 1,
                }
            },
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


def delete(smtp_id: str):
    result = collection.update_one(
        {"_id": ObjectId(smtp_id)},
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


def send_email(email: List[EmailStr], subject: str, body):

    # smtp_server = "smtp.gmail.com"
    # smtp_port = 465
    # smtp_username = "masalasorie@gmail.com"
    # smtp_password = "jyyifooudojlescd"

    AdminSMTPDetails = view_by_status(1)
    if AdminSMTPDetails["status"] == "success" and len(AdminSMTPDetails["data"]) > 0:
        smtp_server = AdminSMTPDetails["data"][0]["smtp_server"]
        smtp_port = AdminSMTPDetails["data"][0]["smtp_port"]
        smtp_username = AdminSMTPDetails["data"][0]["smtp_username"]
        smtp_password = AdminSMTPDetails["data"][0]["smtp_password"]

    sender_email = smtp_username

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = ", ".join(email)
    msg["Subject"] = subject

    msg.attach(MIMEText(body, "html"))

    try:
        # Use SMTP_SSL for port 465
        with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
            server.login(smtp_username, smtp_password)
            server.sendmail(sender_email, email, msg.as_string())
            return {"message": "Email sent successfully", "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}
