from fastapi import FastAPI, UploadFile, File, Depends, Form, Body, Request, BackgroundTasks
from Models.User import UserModel, UserModelUpdate, UserModelAddressUpdate, UserModelBankDetailsUpdate, Token
from Models.Products import ProductModel
from Models.Category import CategoryModel
import services.userService as userService
import services.categoryService as categoryService
import services.productService as productService
import services.locationService as locationService
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
import os
import ast
import uuid
from datetime import datetime
import logging
import json
from typing import List
from fastapi.staticfiles import StaticFiles
from PIL import Image
from os import getcwd


app = FastAPI()
os.makedirs(getcwd() + "/uploads/", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")
# Allow requests from localhost during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://ecomm-python-next.vercel.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)


def resize_image(filename, mainFileName, PATH_FILES):

    sizes = [{
        "width": 100,
        "height": 100,
        "path": '100/'
    }, {
        "width": 300,
        "height": 300,
        "path": '300/'
    }]

    for size in sizes:
        os.makedirs(PATH_FILES+ size['path'], exist_ok=True)
        size_defined = size['width'], size['height']
        image = Image.open(PATH_FILES + mainFileName, mode="r")
        image.thumbnail(size_defined)
        image.save(PATH_FILES+ size['path'] + filename + '.webp', 'webp', optimize = True, quality = 10)
    image = Image.open(PATH_FILES + mainFileName, mode="r")
    image.save(PATH_FILES + filename + '.webp', 'webp', optimize = True, quality = 10)
    # os.remove(PATH_FILES + mainFileName)

# =====================================================================
# ========================= USER ROUTE START ==========================
# =====================================================================


@app.get("/users/")
def get_all():
    return userService.get_all()


@app.get("/users/{product_name}")
def get_user_by_name(user_name: str):
    return userService.get_user_by_name(user_name)


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


@app.post("/token/")
def get_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    return userService.login_for_access_token(form_data)


@app.get("/users/token-details/")
def login_user(token: str):
    return userService.get_current_user(token)

# ADDRESS SECTION START
@app.put("/users/update-address/{user_id}")
def update_address(user_id: str, data: UserModelAddressUpdate = Body(...)):
    return userService.update_address(user_id, data)

@app.delete("/users/address/{user_id}/{address_id}")
def delete_address(user_id: str, address_id:int):
    return userService.delete_address(user_id, address_id)

@app.post("/users/change-address-status/{user_id}/{address_id}")
def change_addresss_status(user_id: str, address_id:int):
    return userService.change_addresss_status(user_id, address_id)
# ADDRESS SECTION END

# BANK SECTION START
@app.put("/users/update-bank-details/{user_id}")
def update_bank(user_id: str, data: UserModelBankDetailsUpdate = Body(...)):
    return userService.update_bank(user_id, data)

@app.delete("/users/bank-details/{user_id}/{bank_id}")
def delete_bank(user_id: str, bank_id:int):
    return userService.delete_bank(user_id, bank_id)

@app.post("/users/change-bank-details-status/{user_id}/{bank_id}")
def change_bank_status(user_id: str, bank_id:int):
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
async def create_product(
    product_data: ProductModel = Body(...),
    cover_image: UploadFile = File(...),
    images: List[UploadFile] = File(...),
):
    try:

        PATH_FILES = getcwd() + "/uploads/products/"
        os.makedirs(PATH_FILES, exist_ok=True)
        cover_image_filename = f"{uuid.uuid1()}-{os.path.splitext(cover_image.filename)[0]}"
        main_cover_image_filename = cover_image_filename + os.path.splitext(cover_image.filename)[1]

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
def get_city_by_country_and_state(country_id: int,state_id: int):
    return locationService.get_city_by_country_and_state(country_id, state_id)


# =====================================================================
# ======================= LOCATION ROUTE END ==========================
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
