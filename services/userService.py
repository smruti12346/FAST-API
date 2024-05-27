from db import db
from bson import ObjectId
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from Models.User import Token

collection = db["user"]

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10


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


def get_all():
    try:
        result = collection.find({"deleted_at": None})
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
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


def update_address(id, data):
    try:
        data = dict(data)
        mainArr = collection.find_one({"_id": ObjectId(id), "deleted_at": None})

        if len(mainArr) > 0:
            address_list = mainArr.get("address", [])
            data["id"] = (
                int(address_list[-1]["id"]) + 1
                if address_list and "id" in address_list[-1]
                else 1
            )
        print(data)
        result = collection.update_one(
            {"_id": ObjectId(id)}, {"$push": {"address": data}}
        )
        if result.modified_count == 1:
            return {"message": "data updated successfully", "status": "success"}
        else:
            return {"message": "failed to update", "status": "error"}
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