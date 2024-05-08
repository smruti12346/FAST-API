from fastapi import FastAPI, UploadFile, File, Depends, Form, Body
from Models.User import UserModel, Token
from Models.Products import ProductModel
from Models.Category import CategoryModel
import services.userService as userService
import services.categoryService as categoryService
import services.productService as productService
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
import os
import ast
import uuid
from datetime import datetime
import logging
import json
from typing import List


app = FastAPI()
# Allow requests from localhost during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)

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
def create_user(user_data: UserModel):
    return userService.create(user_data)


@app.put("/users/{user_id}")
def update_user(user_id: str, user_data: UserModel):
    return userService.update(user_id, user_data)


@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    return userService.delete_user(user_id)


@app.post("/users/login/")
def login_user(email: str, password: str):
    return userService.login(email, password)


@app.post("/token/")
def get_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    return userService.login_for_access_token(form_data)


@app.get("/users/token-details/")
def login_user(token: str):
    return userService.get_current_user(token)


# =====================================================================
# ========================== USER ROUTE END ===========================
# =====================================================================


# =====================================================================
# ======================= CATEGORY ROUTE START ========================
# =====================================================================


@app.get("/category/")
def get_all():
    return categoryService.get_all()


@app.get("/category/{parent_id}")
def get_category_by_parent_id(parent_id: int):
    return categoryService.get_category_by_parent_id(parent_id)


@app.post("/category/")
async def create_category(
    category_data: CategoryModel = Body(...), image: UploadFile = File(...)
):
    try:

        UPLOAD_DIR = "uploads\category"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file = image.filename = f"{uuid.uuid4()}.{os.path.splitext(image.filename)[1]}"
        content = await image.read()
        file_name = os.path.join(UPLOAD_DIR, file)

        with open(file_name, "wb") as f:
            f.write(content)

        if category_data.seo is not None:
            category_data.seo = json.loads(category_data.seo)

        category_data.image = file_name
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
        print(image)
        UPLOAD_DIR = "uploads\category"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        file_name = f"{uuid.uuid4()}{os.path.splitext(image.filename)[1]}"
        file_path = os.path.join(UPLOAD_DIR, file_name)
        with open(file_path, "wb") as f:
            f.write(await image.read())
        category_data.image = file_path
    else:
        category_data.image = existing_category[0]["image"]

    if category_data.seo is not None:
        category_data.seo = json.loads(category_data.seo)
    category_data.created_at = existing_category[0]["created_at"]
    category_data.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    category_data.parent_id = existing_category[0]["parent_id"]
    category_data.parent_id_arr = existing_category[0]["parent_id_arr"]
    return categoryService.update(category_id, category_data)


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
def get_all():
    return productService.get_all()


@app.get("/products/{product_name}")
def get_product_by_name(product_name: str):
    return productService.get_product_by_name(product_name)


@app.post("/products/")
async def create_product(
    product_data: ProductModel = Depends(),
    cover_image: UploadFile = File(...),
    images: List[UploadFile] = File(...),
):
    try:
        UPLOAD_DIR = "uploads\products"
        os.makedirs(UPLOAD_DIR, exist_ok=True)
        # Handle cover image
        cover_image_filename = (
            f"{uuid.uuid4()}{os.path.splitext(cover_image.filename)[1]}"
        )
        cover_image_path = os.path.join(UPLOAD_DIR, cover_image_filename)
        with open(cover_image_path, "wb") as f:
            f.write(await cover_image.read())

        # Handle additional images
        additional_image_filenames = []
        for image in images:
            image_filename = f"{uuid.uuid4()}{os.path.splitext(image.filename)[1]}"
            image_path = os.path.join(UPLOAD_DIR, image_filename)
            with open(image_path, "wb") as f:
                f.write(await image.read())
            additional_image_filenames.append(image_path)

        # Assuming product_data has a field to store image paths
        product_data.cover_image = cover_image_path
        product_data.images = additional_image_filenames

        if product_data.seo is not None:
            product_data.seo = json.loads(product_data.seo)

        # Save product_data to the database or perform other operations
        created_product = productService.create(product_data)
        return created_product
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
