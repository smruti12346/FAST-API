from fastapi import FastAPI, UploadFile, File
from Models.Products import ProductModel
from Models.User import UserModel, Token
import service.productView as productView
import service.userView as userView
from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
import os

app = FastAPI()


# =====================================================================
# ======================= PRODUCT ROUTE START =========================
# =====================================================================


@app.get("/users/")
def get_all():
    return userView.get_all()


@app.get("/users/{product_name}")
def get_user_by_name(user_name: str):
    return userView.get_user_by_name(user_name)


@app.post("/users/")
def create_user(user_data: UserModel, token: str = Depends(userView.get_current_user)):
    return userView.create(user_data)


@app.put("/users/{user_id}")
def update_user(user_id: str, user_data: UserModel):
    return userView.update(user_id, user_data)


@app.delete("/users/{user_id}")
def delete_user(user_id: str):
    return userView.delete_user(user_id)

@app.post("/users/login/")
def login_user(email:str, password:str):
    return userView.login(email, password)

@app.post("/token/")
def get_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    return userView.login_for_access_token(form_data)

@app.get("/users/token-details/")
def login_user(token:str):
    return userView.get_current_user(token)


# =====================================================================
# ======================= PRODUCT ROUTE END ===========================
# =====================================================================


# =====================================================================
# ======================= PRODUCT ROUTE START =========================
# =====================================================================


@app.get("/products/")
def get_all():
    return productView.get_all()


@app.get("/products/{product_name}")
def get_product_by_name(product_name: str):
    return productView.get_product_by_name(product_name)


@app.post("/products/")
def create_product(product_data: ProductModel):
    return productView.create(product_data)


@app.put("/products/{product_id}")
def update_product(product_id: str, product_data: ProductModel):
    return productView.update(product_id, product_data)


@app.delete("/products/{product_id}")
def delete_product(product_id: str):
    return productView.delete_product(product_id)


# =====================================================================
# ======================= PRODUCT ROUTE END ===========================
# =====================================================================
