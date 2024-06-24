from fastapi import FastAPI, UploadFile, File, Depends, Body, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from Models.User import (
    UserModel,
    UserModelUpdate,
    UserModelAddressUpdate,
    UserModelBankDetailsUpdate,
    Token,
)
from Models.Products import ProductModel
from Models.Category import CategoryModel
from Models.Order import OrderModel
from Models.Cart import CartModel
import services.userService as userService
import services.categoryService as categoryService
import services.productService as productService
import services.locationService as locationService
import services.cartService as cartService
import services.orderService as orderService
import services.scripts as scripts
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
import os
import ast
import uuid
from datetime import datetime
import logging
import json
from typing import List, Optional
from fastapi.staticfiles import StaticFiles
from PIL import Image
from os import getcwd
from services.common import convert_oid_to_str

GOOGLE_CLIENT_ID = (
    "758479761027-k52ng36gkobmr9944mqcggtfun8c4si1.apps.googleusercontent.com"
)
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_REDIRECT_URI = "http://127.0.0.1:8000/auth/google/callback"


app = FastAPI()
os.makedirs(getcwd() + "/uploads/", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
# Allow requests from localhost during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://ecomm-python-next.vercel.app",
        "https://python-next-ecommerce-frontend.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


def resize_image(filename, mainFileName, PATH_FILES):

    sizes = [
        {"width": 100, "height": 100, "path": "100/"},
        {"width": 300, "height": 300, "path": "300/"},
    ]

    for size in sizes:
        os.makedirs(PATH_FILES + size["path"], exist_ok=True)
        size_defined = size["width"], size["height"]
        image = Image.open(PATH_FILES + mainFileName, mode="r")
        image.thumbnail(size_defined)
        image.save(
            PATH_FILES + size["path"] + filename + ".webp",
            "webp",
            optimize=True,
            quality=10,
        )
    image = Image.open(PATH_FILES + mainFileName, mode="r")
    image.save(PATH_FILES + filename + ".webp", "webp", optimize=True, quality=10)
    # os.remove(PATH_FILES + mainFileName)


# =====================================================================
# ========================= USER ROUTE START ==========================
# =====================================================================


@app.get("/users/")
def get_all():
    return userService.get_all()


@app.get("/users/{user_name}")
def get_user_by_name(user_name: str):
    return userService.get_user_by_name(user_name)


@app.get("/get-users-by-id/{user_id}")
def get_user_by_id(user_id: str):
    return userService.get_user_by_id(user_id)


# def create_user(user_data: UserModel, token: str = Depends(userService.get_current_user)):
@app.post("/users/")
def create_user(user_data: UserModel = Body(...)):
    return userService.create(user_data)


@app.put("/users/{user_id}")
def update_user(user_id: str, user_data: UserModelUpdate = Body(...)):
    return userService.update(user_id, user_data)


@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    return userService.delete_user(user_id)


@app.post("/users/change-status/{user_id}")
def change_user_status(user_id: str):
    return userService.change_user_status(user_id)


@app.post("/users/login/")
def login_user(email: str, password: str):
    return userService.login(email, password)


@app.get("/auth/google/")
async def auth_google(email: str, password: str, name: str):
    return userService.auth_google(email, password, name)


@app.post("/token/")
def get_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    return userService.login_for_access_token(form_data)


@app.get("/users/token-details/")
def login_user(token: str):
    userDetails = userService.get_current_user(token)
    if userDetails["email"]:
        return {"data": convert_oid_to_str([userDetails]), "status": "success"}
    else:
        return userDetails


@app.post("/users/loggedin-user-deatils/")
def login_user_details(token: str = Depends(userService.get_current_user)):
    if "_id" in token:
        return {"data": convert_oid_to_str([token]), "status": "success"}
    else:
        return {"data": "Not authenticated", "status": "error"}


# ADDRESS SECTION START
@app.put("/users/update-address/{user_id}")
def update_address(user_id: str, data: UserModelAddressUpdate = Body(...)):
    return userService.update_address(user_id, data)


@app.put("/users/update-user-address/")
def update_address(
    token: str = Depends(userService.get_current_user),
    data: UserModelAddressUpdate = Body(...),
):
    if "_id" in token:
        return userService.update_address(str(token["_id"]), data)
    else:
        return {"data": "Not authenticated", "status": "error"}


@app.delete("/users/address/{user_id}/{address_id}")
def delete_address(user_id: str, address_id: int):
    return userService.delete_address(user_id, address_id)


@app.delete("/users/delete-user-address/")
def delete_address(address_id: int, token: str = Depends(userService.get_current_user)):
    if "_id" in token:
        return userService.delete_address(str(token["_id"]), address_id)
    else:
        return {"data": "Not authenticated", "status": "error"}


@app.post("/users/change-address-status/{user_id}/{address_id}")
def change_addresss_status(user_id: str, address_id: int):
    return userService.change_addresss_status(user_id, address_id)


@app.post("/users/change-user-address-status/")
def change_addresss_status(
    address_id: int, token: str = Depends(userService.get_current_user)
):
    if "_id" in token:
        return userService.change_addresss_status(str(token["_id"]), address_id)
    else:
        return {"data": "Not authenticated", "status": "error"}


# ADDRESS SECTION END


# BANK SECTION START
@app.put("/users/update-bank-details/{user_id}")
def update_bank(user_id: str, data: UserModelBankDetailsUpdate = Body(...)):
    return userService.update_bank(user_id, data)


@app.delete("/users/bank-details/{user_id}/{bank_id}")
def delete_bank(user_id: str, bank_id: int):
    return userService.delete_bank(user_id, bank_id)


@app.post("/users/change-bank-details-status/{user_id}/{bank_id}")
def change_bank_status(user_id: str, bank_id: int):
    return userService.change_bank_status(user_id, bank_id)


# BANK SECTION END


# =====================================================================
# ========================== USER ROUTE END ===========================
# =====================================================================


# =====================================================================
# ======================= CATEGORY ROUTE START ========================
# =====================================================================


@app.get("/category/")
def get_all(request: Request):
    return categoryService.get_all(request)


@app.get("/sub-category/")
def get_all_sub_category(request: Request):
    return categoryService.get_all_sub_category(request)


@app.get("/category-wise-product/{page}")
def get_category_wise_product(
    request: Request,
    page: int,
    category_id: int,
    show_page: int,
    sort_by: str = None,
    price_range: str = None,
):
    return categoryService.get_category_wise_product(
        request, page, category_id, show_page, sort_by, price_range
    )


@app.get("/category/{parent_id}")
def get_category_by_parent_id(parent_id: int):
    return categoryService.get_category_by_parent_id(parent_id)


@app.post("/category/")
async def create_category(
    category_data: CategoryModel = Body(...), image: UploadFile = File(...)
):
    try:

        PATH_FILES = getcwd() + "/uploads/category/"
        os.makedirs(PATH_FILES, exist_ok=True)
        filename = f"{uuid.uuid1()}-{os.path.splitext(image.filename)[0]}"
        mainFileName = filename + os.path.splitext(image.filename)[1]

        with open(PATH_FILES + mainFileName, "wb") as myfile:
            content = await image.read()
            myfile.write(content)
            myfile.close()
        resize_image(filename, mainFileName, PATH_FILES)

        if category_data.seo is not None:
            category_data.seo = json.loads(category_data.seo)

        category_data.image = filename + ".webp"
        category_data.parent_id_arr = ast.literal_eval(category_data.parent_id_arr)

        return categoryService.create(category_data)

    except Exception as e:
        logging.error(f"Error occurred while creating category: {e}")
        return {"error": "An error occurred while creating category."}


@app.put("/category/{category_id}")
async def update_category(
    category_id: str,
    category_data: CategoryModel = Body(...),
    image: UploadFile = File(None),
):

    existing_category = categoryService.get(category_id)
    # print(existing_category)

    if existing_category is None:
        return {"message": "data not found for update", "status": "error"}

    if image is not None:
        PATH_FILES = getcwd() + "/uploads/category/"
        os.makedirs(PATH_FILES, exist_ok=True)
        filename = f"{uuid.uuid1()}-{os.path.splitext(image.filename)[0]}"
        mainFileName = filename + os.path.splitext(image.filename)[1]

        with open(PATH_FILES + mainFileName, "wb") as myfile:
            content = await image.read()
            myfile.write(content)
            myfile.close()
        resize_image(filename, mainFileName, PATH_FILES)
        category_data.image = filename + ".webp"
    else:
        category_data.image = existing_category[0]["image"]

    if category_data.seo is not None:
        category_data.seo = json.loads(category_data.seo)
    category_data.created_at = existing_category[0]["created_at"]
    category_data.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    category_data.parent_id = existing_category[0]["parent_id"]
    category_data.parent_id_arr = existing_category[0]["parent_id_arr"]
    return categoryService.update(category_id, category_data)


@app.post("/category/change-status/{category_id}")
def change_category_status(category_id: str):
    return categoryService.change_category_status(category_id)


@app.delete("/category/{category_id}")
def delete_category(category_id: str):
    return categoryService.delete_category(category_id)


# =====================================================================
# ======================= CATEGORY ROUTE END ==========================
# =====================================================================


# =====================================================================
# ======================= PRODUCT ROUTE START =========================
# =====================================================================


@app.get("/products/")
def get_all(request: Request):
    return productService.get_all(request)


@app.get("/products/{product_id}")
def get_product_by_id(request: Request, product_id: str):
    return productService.get_product_by_id(request, product_id)


@app.post("/products/")
async def generate_dummy_product(
    product_data: ProductModel = Body(...),
    cover_image: UploadFile = File(...),
    images: List[UploadFile] = File(...),
):
    try:

        PATH_FILES = getcwd() + "/uploads/products/"
        os.makedirs(PATH_FILES, exist_ok=True)
        cover_image_filename = (
            f"{uuid.uuid1()}-{os.path.splitext(cover_image.filename)[0]}"
        )
        main_cover_image_filename = (
            cover_image_filename + os.path.splitext(cover_image.filename)[1]
        )

        with open(PATH_FILES + main_cover_image_filename, "wb") as myfile:
            content = await cover_image.read()
            myfile.write(content)
            myfile.close()
        resize_image(cover_image_filename, main_cover_image_filename, PATH_FILES)

        additional_image_filenames = []
        for image in images:
            feature_image = f"{uuid.uuid1()}-{os.path.splitext(image.filename)[0]}"
            main_feature_image = feature_image + os.path.splitext(image.filename)[1]

            with open(PATH_FILES + main_feature_image, "wb") as myfile:
                content = await image.read()
                myfile.write(content)
                myfile.close()
                resize_image(feature_image, main_feature_image, PATH_FILES)
            additional_image_filenames.append(feature_image + ".webp")

        product_data.cover_image = cover_image_filename + ".webp"
        product_data.images = additional_image_filenames

        if product_data.seo is not None:
            product_data.seo = json.loads(product_data.seo)
        if product_data.variant is not None:
            product_data.variant = json.loads(product_data.variant)

        # return {"message": product_data, "status": "success"}
        return productService.create(product_data)
    except Exception as e:
        logging.error(f"Error occurred while creating product: {e}")
        return {"error": "An error occurred while creating product."}


@app.put("/products/{product_id}")
def update_product(product_id: str, product_data: ProductModel):
    return productService.update(product_id, product_data)


@app.delete("/products/{product_id}")
def delete_product(product_id: str):
    return productService.delete_product(product_id)


# =====================================================================
# ======================= PRODUCT ROUTE END ===========================
# =====================================================================

# =====================================================================
# ======================= LOCATION ROUTE START ========================
# =====================================================================


@app.get("/get_all_country/")
def get_all_country(request: Request):
    return locationService.get_all_country(request)


@app.get("/get_states_by_country/{country_id}")
def get_states_by_country(country_id: int):
    return locationService.get_states_by_country(country_id)


@app.get("/get_city_by_country_and_state/{country_id}/{state_id}")
def get_city_by_country_and_state(country_id: int, state_id: int):
    return locationService.get_city_by_country_and_state(country_id, state_id)


# =====================================================================
# ======================= LOCATION ROUTE END ==========================
# =====================================================================


# =====================================================================
# ======================= ORDER ROUTE START ===========================
# =====================================================================


@app.post("/add_to_cart/")
def add_to_cart(product_id: str, token: str = Depends(userService.get_current_user)):
    if "_id" in token:
        return cartService.add_to_cart(str(token["_id"]), product_id)
    else:
        return {"data": "Not authenticated", "status": "error"}


@app.post("/cart/")
def add_to_cart(request: Request, items: List[str] = Body(...)):
    return cartService.get_cart_details_by_product_arr(request, items)


@app.post("/get_all_cart_details_by_user_id/")
def get_all_cart_details_by_user_id(
    request: Request, token: str = Depends(userService.get_current_user)
):
    if "_id" in token:
        return cartService.get_all_cart_details_by_user_id(request, str(token["_id"]))
    else:
        return {"data": "Not authenticated", "status": "error"}


# @app.post("/get_all_cart_details_by_user_id/")
# def get_all_cart_details_by_user_id(request: Request, user_id: str):
#     return cartService.get_all_cart_details_by_user_id(request, user_id)


@app.post("/check_order_quantity/")
def check_order_quantity(product_id: str, varientArr: List[int]):
    return orderService.check_order_quantity(product_id, varientArr)

@app.post("/check_order_quantity_by_order/")
def check_order_quantity_by_order(product_details: List[OrderModel] = Body(...)):
    return orderService.check_order_quantity_by_order(product_details)


@app.post("/order_placed/")
def order_placed(
    product_details: List[OrderModel] = Body(...),
    token: str = Depends(userService.get_current_user),
):
    if "_id" in token:
        return orderService.order_placed(str(token["_id"]), product_details)
    else:
        return {"data": "Not authenticated", "status": "error"}


@app.get("/orders/")
def get_all_orders(request: Request):
    return orderService.get_all_orders(request)


# =====================================================================
# ======================= ORDER ROUTE END =============================
# =====================================================================


@app.post("/test-file-upload/")
async def create_product(
    cover_image: UploadFile = File(...),
):
    try:
        PATH_FILES = getcwd() + "/uploads/test/"
        os.makedirs(PATH_FILES, exist_ok=True)
        filename = f"{uuid.uuid1()}-{os.path.splitext(cover_image.filename)[0]}"
        mainFileName = filename + os.path.splitext(cover_image.filename)[1]
        with open(PATH_FILES + mainFileName, "wb") as myfile:
            content = await cover_image.read()
            myfile.write(content)
            myfile.close()
        resize_image(filename, mainFileName, PATH_FILES)
        return {"message": "image", "status": "success"}
    except Exception as e:
        logging.error(f"Error occurred while creating product: {e}")
        return {"error": "An error occurred while creating product."}


# @app.post("/generate-dummy-category/")
# def generate_dummy_category():
#     return scripts.generate_dummy_category()


@app.post("/generate-dummy-product/")
def generate_dummy_product():
    return scripts.generate_dummy_product()
