from fastapi import APIRouter, Depends, Body
import services.userService as userService
from Models.User import (
    UserModel,
    UserModelUpdate,
    UserModelAddressUpdate,
    UserModelBankDetailsUpdate,
    Token,
)
from fastapi.security import OAuth2PasswordRequestForm
from services.common import convert_oid_to_str

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


@router.get("/get-users-by-id/", tags=["USER MANAGEMENT"])
def get_user_by_token(token: str = Depends(userService.get_current_user)):
    if "_id" in token:
        return userService.get_user_by_id(str(token["_id"]))
    else:
        return {"data": "Not authenticated", "status": "error"}


@router.get("/get-users-by-id/{user_id}", tags=["USER MANAGEMENT"])
def get_user_by_id(user_id: str):
    return userService.get_user_by_id(user_id)


@router.put("/users/{user_id}", tags=["USER MANAGEMENT"])
def update_user(user_id: str, user_data: UserModelUpdate = Body(...)):
    return userService.update(user_id, user_data)


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
        return {"data": "Not authenticated", "status": "error"}


# ======================================================================================================
# ======================================================================================================
# ======================================================================================================


# ADDRESS SECTION START
@router.put("/users/update-address/{user_id}", tags=["USER ADDRESS MANAGEMENT"])
def update_address(user_id: str, data: UserModelAddressUpdate = Body(...)):
    return userService.update_address(user_id, data)


@router.put("/users/update-user-address/", tags=["USER ADDRESS MANAGEMENT"])
def update_address(
    token: str = Depends(userService.get_current_user),
    data: UserModelAddressUpdate = Body(...),
):
    if "_id" in token:
        return userService.update_address(str(token["_id"]), str(token["email"]), data)
    else:
        return {"data": "Not authenticated", "status": "error"}


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
        return {"data": "Not authenticated", "status": "error"}


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
        return {"data": "Not authenticated", "status": "error"}


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
