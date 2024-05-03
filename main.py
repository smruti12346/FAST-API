from fastapi import FastAPI, UploadFile, File
from Models.User import UserModel, Token
from Models.Products import ProductModel
from Models.Category import CategoryModel
import services.userService as userService
import services.categoryService as categoryService
import services.productService as productService
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
import os

app = FastAPI()


# =====================================================================
# ========================= USER ROUTE START ==========================
# =====================================================================


@app.get("/users/")
def get_all():
    return userService.get_all()


@app.get("/users/{product_name}")
def get_user_by_name(user_name: str):
    return userService.get_user_by_name(user_name)


@app.post("/users/")
def create_user(user_data: UserModel, token: str = Depends(userService.get_current_user)):
    return userService.create(user_data)


@app.put("/users/{user_id}")
def update_user(user_id: str, user_data: UserModel):
    return userService.update(user_id, user_data)


@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    return userService.delete_user(user_id)

@app.post("/users/login/")
def login_user(email:str, password:str):
    return userService.login(email, password)

@app.post("/token/")
def get_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    return userService.login_for_access_token(form_data)

@app.get("/users/token-details/")
def login_user(token:str):
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
    return categoryService.get_category_by_id(parent_id)


@app.post("/category/")
def create_category(category_data: CategoryModel):
    return categoryService.create(category_data)


@app.put("/category/{category_id}")
def update_category(category_id: str, category_data: CategoryModel):
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
def create_product(product_data: ProductModel):
    return productService.create(product_data)


@app.put("/products/{product_id}")
def update_product(product_id: str, product_data: ProductModel):
    return productService.update(product_id, product_data)


@app.delete("/products/{product_id}")
def delete_product(product_id: str):
    return productService.delete_product(product_id)


# =====================================================================
# ======================= PRODUCT ROUTE END ===========================
# =====================================================================
