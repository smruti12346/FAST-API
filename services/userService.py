from db import db
from bson import ObjectId
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from Models.User import Token
import requests
from pydantic import Field
import services.shippingService as shippingService
import services.locationService as locationService
from .common import paginate


collection = db["user"]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 720


GOOGLE_CLIENT_ID = (
    "758479761027-k52ng36gkobmr9944mqcggtfun8c4si1.apps.googleusercontent.com"
)
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_REDIRECT_URI = "http://127.0.0.1:8000/auth/google/callback"


def check_email_exist(email: str):
    user = collection.find_one({"email": email})
    return user


def create(user_data):
    try:
        user_data = dict(user_data)
        if check_email_exist(user_data["email"]) is None:
            user_data["password"] = pwd_context.hash(user_data["password"])
            result = collection.insert_one(user_data)
            return {
                "message": "data inserted successfully",
                "_id": str(result.inserted_id),
                "status": "success",
            }
        else:
            return {"message": "user already exists", "status": "error"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_all(page, show_page):
    try:
        # result = collection.find({"deleted_at": None})
        # data = []
        # for doc in result:
        #     doc["_id"] = str(doc["_id"])
        #     data.append(doc)

        pipeline = [
            {"$match": {"deleted_at": None}},
            {"$sort": {"created_at": 1}},
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "deleted_at": 1,
                    "name": 1,
                    "email": 1,
                    "mobile": 1,
                    "dob": 1,
                    "gender": 1,
                    "profile_image": 1,
                    "address": 1,
                    "bank_details": 1,
                    "user_type": 1,
                    "user_permission": 1,
                    "description": 1,
                    "status": 1,
                    "created_at": 1,
                    "created_by": 1,
                    "updated_at": 1,
                    "updated_by": 1,
                }
            },
        ]
        result = paginate(collection, pipeline, page, show_page)
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_user_by_name(user_name):
    try:
        result = collection.find({"name": user_name})
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_user_by_id(id):
    try:
        result = list(collection.find({"_id": ObjectId(id), "deleted_at": None}))
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def merge_objects(obj1, obj2):
    merged_obj = obj1.copy()
    for key, value in obj2.items():
        if key in merged_obj and merged_obj[key] is None:
            merged_obj[key] = value
    return merged_obj


def update(id, data):
    try:
        data = dict(data)
        updated_data = merge_objects(data, get_user_by_id(id)["data"][0])
        result = collection.update_one({"_id": ObjectId(id)}, {"$set": updated_data})
        if result.modified_count == 1:
            return {"message": "data updated successfully", "status": "success"}
        else:
            return {"message": "failed to update", "status": "error"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def delete_user(user_id: str):
    result = collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"deleted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}},
    )
    if result.modified_count == 1:
        return {"message": "data deleted successfully", "status": "success"}
    else:
        return {"message": "failed to delete", "status": "error"}


def change_user_status(user_id: str):
    getStatus = get_user_by_id(user_id)["data"][0]["status"]
    if getStatus == 0:
        status = 1
    else:
        status = 0

    result = collection.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"status": status}},
    )
    if result.modified_count == 1:
        return {"message": "status changed successfully", "status": "success"}
    else:
        return {"message": "failed to change status", "status": "error"}


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def login(email, password: str):
    try:
        user = check_email_exist(email)
        if user is not None:
            if pwd_context.verify(password, user["password"]):
                access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
                access_token = create_access_token(
                    data={"sub": user["email"]}, expires_delta=access_token_expires
                )
                return {
                    "message": "login successfully",
                    "access_token": access_token,
                    "name": user["name"],
                    "email": email,
                    "user_type": user["user_type"],
                    "token_type": "bearer",
                    "status": "success",
                }
            else:
                return {"message": "password not match", "status": "error"}
        else:
            return {"message": "invalid user creadential", "status": "error"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def auth_google(email, password, name):
    try:
        if check_email_exist(email) is None:
            user_data = {
                "email": email,
                "name": name,
                "mobile": None,
                "password": pwd_context.hash(password),
                "dob": None,
                "gender": None,
                "profile_image": None,
                "address": [],
                "bank_details": [],
                "user_type": 2,
                "user_permission": None,
                "description": None,
                "status": 1,
                "deleted_at": None,
                "created_at": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                "created_date": str(datetime.now().strftime("%Y-%m-%d")),
                "created_time": str(datetime.now().strftime("%H:%M:%S")),
                "created_by": None,
                "updated_at": None,
                "updated_by": None,
            }
            collection.insert_one(user_data)

        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": email}, expires_delta=access_token_expires
        )

        return {
            "message": "login successfully",
            "access_token": access_token,
            "name": name,
            "email": email,
            "user_type": 1,
            "token_type": "bearer",
            "status": "success",
        }
    except Exception as e:
        return {"message": str(e), "status": "error"}


def login_for_access_token(form_data):
    print(form_data.username)
    # Authenticate the user
    user = check_email_exist(form_data.username)
    if user is not None:
        if pwd_context.verify(form_data.password, user["password"]):
            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user["email"]}, expires_delta=access_token_expires
            )
            return Token(access_token=access_token, token_type="bearer")
    else:
        return {"message": "invalid user creadential", "status": "error"}


def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        user = check_email_exist(email)
        return user
    except JWTError as e:
        return {"message": str(e), "status": "error"}
        # return {"message": "Could not validate credentials", "status": "error"}


def get_address_by_id(id):
    try:
        result = list(collection.find({"_id": ObjectId(id), "deleted_at": None}))
        return {"data": result[0]["address"], "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def update_address(id, email, data):
    try:
        data = dict(data)
        # print(data)
        # country_details = locationService.get_country_by_id(data["country_id"])["data"]
        # state_details = locationService.get_states_by_state_id_and_country_id(
        #     data["country_id"], data["state_id"]
        # )["data"]
        # city_details = locationService.get_city_by_city_id_country_id_and_state_id(
        #     data["country_id"], data["state_id"], data["city_id"]
        # )["data"]

        # if country_details and len(country_details) > 0:
        #     country_iso = country_details[0]["name"]
        # else:
        #     return {"message": "Country not found", "status": "error"}

        # if state_details and len(state_details) > 0:
        #     state_code = state_details[0]["state_code"]
        # else:
        #     return {"message": "Country not found", "status": "error"}

        # if city_details and len(city_details) > 0:
        #     city_name = city_details[0]["name"]
        # else:
        #     return {"message": "Country not found", "status": "error"}

        shippingDetails = shippingService.validate_address(
            data["roadName_area_colony"],
            data["city_name"],
            data["state_code"],
            data["pin_number"],
            data["country_code"],
            email,
            data["phone_number"],
        )

        if (
            shippingDetails["status"] != "error"
            and shippingDetails["data"]["verifications"]["delivery"]["success"] == True
        ):
            mainArr = collection.find_one({"_id": ObjectId(id), "deleted_at": None})

            if len(mainArr) > 0:
                address_list = mainArr.get("address", [])
                data["id"] = (
                    int(address_list[-1]["id"]) + 1
                    if address_list and "id" in address_list[-1]
                    else 1
                )
            # print(data)
            result = collection.update_one(
                {"_id": ObjectId(id)}, {"$push": {"address": data}}
            )

            if result.modified_count == 1:
                return {"message": "data updated successfully", "status": "success"}
            else:
                return {"message": "failed to update", "status": "error"}
        else:
            return shippingDetails

    except Exception as e:
        return {"message": str(e), "status": "error"}


def delete_address(user_id: str, user_address_id: int):
    user = collection.find_one(
        {"_id": ObjectId(user_id), "address.id": user_address_id}, {"address.$": 1}
    )
    if len(user) > 0:
        query = {"_id": ObjectId(user_id), "address.id": user_address_id}
        update = {
            "$set": {
                "address.$.deleted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        result = collection.update_one(query, update)
        if result.modified_count == 1:
            return {"message": "deleted successfully", "status": "success"}
        else:
            return {"message": "failed to delete", "status": "error"}
    else:
        return {"message": "user address not found", "status": "error"}


def change_addresss_status(user_id: str, user_address_id: int):

    user = collection.find_one(
        {"_id": ObjectId(user_id), "address.id": user_address_id}, {"address.$": 1}
    )

    if len(user) > 0:
        collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": {"address.$[].primary_status": 0}}
        )
        if user["address"][0]["primary_status"] == 0:
            status = 1
        elif user["address"][0]["primary_status"] == 1:
            status = 0
        query = {"_id": ObjectId(user_id), "address.id": user_address_id}
        update = {"$set": {"address.$.primary_status": status}}
        collection.update_one(query, update)
        return {"message": "status changed successfully", "status": "success"}
    else:
        return {"message": "user address not found", "status": "error"}


def get_bank_details_by_id(id):
    try:
        result = list(collection.find({"_id": ObjectId(id), "deleted_at": None}))
        return {"data": result[0]["bank_details"], "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def update_bank(id, data):
    try:
        data = dict(data)
        mainArr = collection.find_one({"_id": ObjectId(id), "deleted_at": None})

        if len(mainArr) > 0:
            bank_details_list = mainArr.get("bank_details", [])
            data["id"] = (
                int(bank_details_list[-1]["id"]) + 1
                if bank_details_list and "id" in bank_details_list[-1]
                else 1
            )
        print(data)
        result = collection.update_one(
            {"_id": ObjectId(id)}, {"$push": {"bank_details": data}}
        )
        if result.modified_count == 1:
            return {"message": "data updated successfully", "status": "success"}
        else:
            return {"message": "failed to update", "status": "error"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def delete_bank(user_id: str, bank_id: int):
    user = collection.find_one(
        {"_id": ObjectId(user_id), "bank_details.id": bank_id}, {"bank_details.$": 1}
    )
    if len(user) > 0:
        query = {"_id": ObjectId(user_id), "bank_details.id": bank_id}
        update = {
            "$set": {
                "bank_details.$.deleted_at": datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            }
        }
        result = collection.update_one(query, update)
        if result.modified_count == 1:
            return {"message": "deleted successfully", "status": "success"}
        else:
            return {"message": "failed to delete", "status": "error"}
    else:
        return {"message": "user's bank details not found", "status": "error"}


def change_bank_status(user_id: str, bank_id: int):

    user = collection.find_one(
        {"_id": ObjectId(user_id), "bank_details.id": bank_id}, {"bank_details.$": 1}
    )

    if len(user) > 0:
        collection.update_one(
            {"_id": ObjectId(user_id)}, {"$set": {"bank_details.$[].primary_status": 0}}
        )
        if user["bank_details"][0]["primary_status"] == 0:
            status = 1
        elif user["bank_details"][0]["primary_status"] == 1:
            status = 0
        query = {"_id": ObjectId(user_id), "bank_details.id": bank_id}
        update = {"$set": {"bank_details.$.primary_status": status}}
        collection.update_one(query, update)
        return {"message": "status changed successfully", "status": "success"}
    else:
        return {"message": "user bank's details not found", "status": "error"}
