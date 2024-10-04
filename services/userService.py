from db import db
from bson import ObjectId
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated
from fastapi import Depends, Request
from fastapi.security import OAuth2PasswordBearer
from Models.User import Token
from pydantic import Field
import services.shippingService as shippingService
import services.smtpService as smtpService
from .common import paginate
import random
from urllib.parse import urlparse


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

            access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
            access_token = create_access_token(
                data={"sub": user_data["email"]}, expires_delta=access_token_expires
            )

            return {
                "message": "Registration Successful",
                "access_token": access_token,
                "name": user_data["name"],
                "email": user_data["email"],
                "user_type": 1,
                "token_type": "bearer",
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


def get_user_by_id(request, id):
    try:
        pipeline = [
            {"$match": {"_id": ObjectId(id), "deleted_at": None}},
            {"$unwind": "$address"},
            {
                "$lookup": {
                    "from": "countries", 
                    "localField": "address.country_code",
                    "foreignField": "code",
                    "as": "country_info",
                }
            },
            {
                "$group": {
                    "_id": "$_id",
                    "email": {"$first": "$email"},
                    "name": {"$first": "$name"},
                    "mobile": {"$first": "$mobile"},
                    "dob": {"$first": "$dob"},
                    "gender": {"$first": "$gender"},
                    "profile_image": {"$first": "$profile_image"},
                    "user_type": {"$first": "$user_type"},
                    "status": {"$first": "$status"},
                    "created_at": {"$first": "$created_at"},
                    "updated_at": {"$first": "$updated_at"},
                    "created_date": {"$first": "$created_date"},
                    "address": {
                        "$push": {
                            "full_name": "$address.full_name",
                            "phone_number": "$address.phone_number",
                            "country_code": "$address.country_code",
                            "state_code": "$address.state_code",
                            "city_name": "$address.city_name",
                            "pin_number": "$address.pin_number",
                            "roadName_area_colony": "$address.roadName_area_colony",
                            "house_bulding_name": "$address.house_bulding_name",
                            "landmark": "$address.landmark",
                            "primary_status": "$address.primary_status",
                            "status": "$address.status",
                            "id": "$address.id",
                            "country_info": {
                                "$arrayElemAt": ["$country_info", 0]
                            },  # Example for country info if available
                        }
                    },
                }
            },
            # Add fields for image URLs
            {
                "$addFields": {
                    "profile_image_url": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/user/",
                            "$profile_image",
                        ]
                    },
                    "profile_image_url_100": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/user/100/",
                            "$profile_image",
                        ]
                    },
                    "profile_image_url_300": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/user/300/",
                            "$profile_image",
                        ]
                    },
                }
            },
            # Format the _id field as a string
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "email": 1,
                    "name": 1,
                    "mobile": 1,
                    "dob": 1,
                    "gender": 1,
                    "user_type": 1,
                    "status": 1,
                    "created_at": 1,
                    "created_date": 1,
                    "updated_at": 1,
                    "address": 1,  # Include address array
                    "profile_image_url": 1,
                    "profile_image_url_100": 1,
                    "profile_image_url_300": 1,
                }
            },
        ]

        result = list(collection.aggregate(pipeline))
        return {"data": result, "status": "success"}
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
        if data.get('profile_image') is None:
            del data['profile_image']

        updated_data = merge_objects(data, get_user_by_id(Request, id)["data"][0])
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
    getStatus = get_user_by_id(Request, user_id)["data"][0]["status"]
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

                # Set the id and status based on the presence of the address list and "id"
                if address_list and "id" in address_list[-1]:
                    data["id"] = int(address_list[-1]["id"]) + 1
                    data["primary_status"] = (
                        0  # status = 0 if "id" exists in the last item
                    )
                else:
                    data["id"] = 1
                    data["primary_status"] = 1  # status = 1 otherwise
            # print(data)
            result = collection.update_one(
                {"_id": ObjectId(id)}, {"$push": {"address": data}}
            )

            if result.modified_count == 1:
                return {"message": "Address added successfully", "status": "success"}
            else:
                return {"message": "failed to add address", "status": "error"}
        else:
            return shippingDetails

    except Exception as e:
        return {"message": str(e), "status": "error"}


def update_address_using_id(id, email, data):
    try:
        data = dict(data)
        print(id)
        print(email)
        print(data)
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
            # mainArr = collection.find_one({"_id": ObjectId(id), "deleted_at": None})

            # if len(mainArr) > 0:
            #     address_list = mainArr.get("address", [])

            #     # Set the id and status based on the presence of the address list and "id"
            #     if address_list and "id" in address_list[-1]:
            #         data["id"] = int(address_list[-1]["id"]) + 1
            #         data["primary_status"] = (
            #             0  # status = 0 if "id" exists in the last item
            #         )
            #     else:
            #         data["id"] = 1
            #         data["primary_status"] = 1  # status = 1 otherwise
            # # print(data)

            address_id = data["id"]
            data.pop("id", None)
            result = collection.update_one(
                {"_id": ObjectId(id), "address.id": address_id},
                {"$set": {f"address.$.{key}": value for key, value in data.items()}},
            )
            if result.modified_count == 1:
                return {"message": "Address added successfully", "status": "success"}
            else:
                return {"message": "failed to add address", "status": "error"}
        else:
            return shippingDetails

    except Exception as e:
        return {"message": str(e), "status": "error"}


# def delete_address(user_id: str, user_address_id: int):
#     user = collection.find_one(
#         {"_id": ObjectId(user_id), "address.id": user_address_id}, {"address.$": 1}
#     )
#     if len(user) > 0:
#         query = {"_id": ObjectId(user_id), "address.id": user_address_id}
#         update = {
#             "$set": {
#                 "address.$.deleted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#             }
#         }
#         result = collection.update_one(query, update)
#         if result.modified_count == 1:
#             return {"message": "deleted successfully", "status": "success"}
#         else:
#             return {"message": "failed to delete", "status": "error"}
#     else:
#         return {"message": "user address not found", "status": "error"}


def delete_address(user_id: str, user_address_id: int):
    user = collection.find_one(
        {"_id": ObjectId(user_id), "address.id": user_address_id}, {"address.$": 1}
    )
    if user:
        query = {"_id": ObjectId(user_id)}
        update = {"$pull": {"address": {"id": user_address_id}}}
        result = collection.update_one(query, update)
        if result.modified_count == 1:
            return {"message": "Address deleted successfully", "status": "success"}
        else:
            return {"message": "Failed to delete the address", "status": "error"}
    else:
        return {"message": "User address not found", "status": "error"}


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


def forget_password_link_send(user_email: str, request):
    try:
        otp = "".join([str(random.randint(0, 9)) for _ in range(6)])

        user = check_email_exist(user_email)
        if user is not None:
            user_id = str(user["_id"])
            url = str(request.base_url)[:-1]
            parsed_url = urlparse(url)
            mainUrl = f"{parsed_url.hostname}"

            result = collection.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": {"forget_password_otp": int(otp)}},
            )

            body = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Password Reset OTP</title>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        background-color: #f4f4f4;
                        margin: 0;
                        padding: 20px;
                    }}
                    .container {{
                        max-width: 600px;
                        margin: auto;
                        background: white;
                        padding: 20px;
                        border-radius: 5px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    h2 {{
                        color: #333;
                    }}
                    p {{
                        color: #555;
                    }}
                    .otp {{
                        font-size: 24px;
                        font-weight: bold;
                        color: #007BFF;
                    }}
                    .footer {{
                        margin-top: 20px;
                        font-size: 12px;
                        color: #888;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <h2>Password Reset Request</h2>
                    <p>Hi {user['name']},</p>
                    <p>We received a request to reset your password. Please use the One-Time Password (OTP) below to proceed:</p>
                    
                    <p class="otp">{otp}</p>

                    <p>This OTP is valid for a limited time only. If you did not request a password reset, please ignore this email.</p>

                    <p>
                        Thank you,<br> 
                        {mainUrl}                   
                    </p>

                    <div class="footer">
                        <p>If you have any questions, feel free to contact our support team.</p>
                    </div>
                </div>
            </body>
            </html>"""
            if result.modified_count == 1:
                smtpService.send_email(
                    user_email, "One-Time Password for Password Reset", body
                )
                return {"message": "Email sent successfully", "status": "success"}
            else:
                return {"message": "failed to change status", "status": "error"}
        else:
            return {
                "message": "this user is not exist",
                "status": "fail",
            }
    except Exception as e:
        return {"message": str(e), "status": "error"}


def reset_password_with_otp(
    user_email: str, password: str, confirm_password: str, otp: int
):
    try:
        user = check_email_exist(user_email)
        if user is not None:
            user_id = str(user["_id"])
            if password == confirm_password:
                if user["forget_password_otp"] == otp:
                    result = collection.update_one(
                        {"_id": ObjectId(user_id)},
                        {
                            "$set": {
                                "password": pwd_context.hash(password),
                                "forget_password_otp": None,
                            }
                        },
                    )
                    if result.modified_count == 1:
                        return {
                            "message": "password changed successfully",
                            "status": "success",
                        }
                    else:
                        return {"message": "failed to change status", "status": "error"}
                else:
                    return {"message": "invalid otp", "status": "error"}
            else:
                return {
                    "message": "password and confirm password are not match",
                    "status": "error",
                }
        else:
            return {
                "message": "this user is not exist",
                "status": "fail",
            }
    except Exception as e:
        return {"message": str(e), "status": "error"}
