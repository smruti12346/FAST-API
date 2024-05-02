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
ACCESS_TOKEN_EXPIRE_MINUTES = 1


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
        return {"message": e, "status": "error"}


def get_all():
    try:
        result = collection.find()
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": e, "status": "error"}


def get_user_by_name(user_name):
    try:
        result = collection.find({"name": user_name})
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": e, "status": "error"}


def update(id, data):
    try:
        data = dict(data)
        result = collection.update_one({"_id": ObjectId(id)}, {"$set": data})
        if result.modified_count == 1:
            return {"message": "data updated successfully", "status": "success"}
        else:
            return {"message": "failed to update", "status": "error"}
    except Exception as e:
        return {"message": e, "status": "error"}


def delete_user(user_id: str):
    result = collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 1:
        return {"message": "data deleted successfully", "status": "success"}
    else:
        return {"message": "failed to delete", "status": "error"}


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
                    "token_type": "bearer",
                    "status": "success",
                }
            else:
                return {"message": "password not match", "status": "error"}
        else:
            return {"message": "invalid user creadential", "status": "error"}
    except Exception as e:
        return {"message": e, "status": "error"}


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
        # print(email)
    except JWTError:
        return {"message": "Could not validate credentials", "status": "error"}
    # return user
