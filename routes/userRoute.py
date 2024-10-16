from fastapi import APIRouter, Depends, Body, Request, UploadFile, File
import services.userService as userService
from Models.User import (
    UserModel,
    UserModelUpdate,
    UserModelAddressUpdate,
    UserModelBankDetailsUpdate,
    Token,
    UserModelAddressUpdateById,
)
from fastapi.security import OAuth2PasswordRequestForm
from services.common import convert_oid_to_str
from typing import Optional
from os import getcwd
import os
import uuid
from services.common import resize_image

router = APIRouter()


# def create_user(user_data: UserModel, token: str = Depends(userService.get_current_user)):
@router.post("/users/", tags=["USER MANAGEMENT"])
def create_user(user_data: UserModel = Body(...)):
    return userService.create(user_data)


@router.get("/users/{page}", tags=["USER MANAGEMENT"])
def get_all(page: int, show_page: int):
    return userService.get_all(page, show_page)


@router.get("/users/{user_name}", tags=["USER MANAGEMENT"])
def get_user_by_name(user_name: str):
    return userService.get_user_by_name(user_name)


@router.get("/get-users-by-id", tags=["USER MANAGEMENT"])
def get_user_by_token(
    request: Request, token: str = Depends(userService.get_current_user)
):
    if "_id" in token:
        return userService.get_user_by_id(request, str(token["_id"]))
    else:
        return {"message": "Please Login First", "status": "error"}


@router.get("/get-users-by-id/{user_id}", tags=["USER MANAGEMENT"])
def get_user_by_id(user_id: str):
    return userService.get_user_by_id(user_id)


@router.put("/users", tags=["USER MANAGEMENT"])
async def update_user(
    user_data: UserModelUpdate = Body(...),
    profile_image: Optional[UploadFile] = File(None),
    token: str = Depends(userService.get_current_user),
):
    try:
        if "_id" in token:
            if profile_image is not None and profile_image != "":
                PATH_FILES = getcwd() + "/uploads/user/"
                os.makedirs(PATH_FILES, exist_ok=True)
                filename = (
                    f"{uuid.uuid1()}-{os.path.splitext(profile_image.filename)[0]}"
                )
                mainFileName = filename + os.path.splitext(profile_image.filename)[1]
                with open(PATH_FILES + mainFileName, "wb") as myfile:
                    content = await profile_image.read()
                    myfile.write(content)
                    myfile.close()
                resize_image(filename, mainFileName, PATH_FILES)
                user_data.profile_image = filename + ".webp"
            return userService.update(str(token["_id"]), user_data)
        else:
            return {"message": "Please Login First", "status": "error"}
    except Exception as e:
        return {"error": str(e)}


@router.delete("/users/{user_id}", tags=["USER MANAGEMENT"])
def delete_user(user_id: str):
    return userService.delete_user(user_id)


@router.post("/users/change-status/{user_id}", tags=["USER MANAGEMENT"])
def change_user_status(user_id: str):
    return userService.change_user_status(user_id)


# ======================================================================================================
# ======================================================================================================
# ======================================================================================================


@router.post("/users/login/", tags=["USER AUTHENTICATION"])
def login_user(email: str, password: str):
    return userService.login(email, password)


@router.get("/auth/google/", tags=["USER AUTHENTICATION"])
async def auth_google(email: str, password: str, name: str):
    return userService.auth_google(email, password, name)


@router.post("/token/", tags=["USER AUTHENTICATION"])
def get_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    return userService.login_for_access_token(form_data)


@router.get("/users/token-details/", tags=["USER AUTHENTICATION"])
def login_user(token: str):
    userDetails = userService.get_current_user(token)
    if userDetails["email"]:
        return {"data": convert_oid_to_str([userDetails]), "status": "success"}
    else:
        return userDetails


@router.post("/users/loggedin-user-deatils/", tags=["USER AUTHENTICATION"])
def login_user_details(token: str = Depends(userService.get_current_user)):
    if "_id" in token:
        return {"data": convert_oid_to_str([token]), "status": "success"}
    else:
        return {"message": "Please Login First", "status": "error"}


# ======================================================================================================
# ======================================================================================================
# ======================================================================================================


# ADDRESS SECTION START
# @router.put("/users/update-address/{user_id}", tags=["USER ADDRESS MANAGEMENT"])
# def update_address(user_id: str, data: UserModelAddressUpdate = Body(...)):
#     return userService.update_address(user_id, data)


@router.put("/users/update-user-address/", tags=["USER ADDRESS MANAGEMENT"])
def update_address(
    token: str = Depends(userService.get_current_user),
    data: UserModelAddressUpdate = Body(...),
):
    if "_id" in token:
        return userService.update_address(str(token["_id"]), str(token["email"]), data)
    else:
        return {"message": "Please Login First", "status": "error"}


# ADDRESS SECTION START
@router.put("/users/update-address-using-id/", tags=["USER ADDRESS MANAGEMENT"])
def update_address_using_id(
    token: str = Depends(userService.get_current_user),
    data: UserModelAddressUpdateById = Body(...),
):
    if "_id" in token:
        return userService.update_address_using_id(
            str(token["_id"]), str(token["email"]), data
        )
    else:
        return {"message": "Please Login First", "status": "error"}


@router.delete(
    "/users/address/{user_id}/{address_id}", tags=["USER ADDRESS MANAGEMENT"]
)
def delete_address(user_id: str, address_id: int):
    return userService.delete_address(user_id, address_id)


@router.delete("/users/delete-user-address/", tags=["USER ADDRESS MANAGEMENT"])
def delete_address(address_id: int, token: str = Depends(userService.get_current_user)):
    if "_id" in token:
        return userService.delete_address(str(token["_id"]), address_id)
    else:
        return {"message": "Please Login First", "status": "error"}


# @router.post("/users/change-address-status/{user_id}/{address_id}", tags=['USER ADDRESS MANAGEMENT'])
# def change_addresss_status(user_id: str, address_id: int):
#     return userService.change_addresss_status(user_id, address_id)


@router.post("/users/change-user-address-status/", tags=["USER ADDRESS MANAGEMENT"])
def change_addresss_status(
    address_id: int, token: str = Depends(userService.get_current_user)
):
    if "_id" in token:
        return userService.change_addresss_status(str(token["_id"]), address_id)
    else:
        return {"message": "Please Login First", "status": "error"}


# ADDRESS SECTION END

# ======================================================================================================
# ======================================================================================================
# ======================================================================================================
# BANK SECTION START


@router.put(
    "/users/update-bank-details/{user_id}", tags=["USER BANK DETAILS MANAGEMENT"]
)
def update_bank(user_id: str, data: UserModelBankDetailsUpdate = Body(...)):
    return userService.update_bank(user_id, data)


@router.delete(
    "/users/bank-details/{user_id}/{bank_id}", tags=["USER BANK DETAILS MANAGEMENT"]
)
def delete_bank(user_id: str, bank_id: int):
    return userService.delete_bank(user_id, bank_id)


@router.post(
    "/users/change-bank-details-status/{user_id}/{bank_id}",
    tags=["USER BANK DETAILS MANAGEMENT"],
)
def change_bank_status(user_id: str, bank_id: int):
    return userService.change_bank_status(user_id, bank_id)


# BANK SECTION END


@router.post("/forgot-password/send-otp", tags=["FORGET PASSWORD MANAGEMNT"])
def forget_password_link_send(user_email: str, request: Request):
    return userService.forget_password_link_send(user_email, request)


@router.post("/forgot-password/verify-otp", tags=["FORGET PASSWORD MANAGEMNT"])
def reset_password_with_otp(
    user_email: str, password: str, confirm_password: str, otp: int
):
    return userService.reset_password_with_otp(
        user_email, password, confirm_password, otp
    )
