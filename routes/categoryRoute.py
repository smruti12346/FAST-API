from fastapi import APIRouter, UploadFile, File, Body, Request
import services.categoryService as categoryService
from typing import Optional
from Models.Category import CategoryModel
from os import getcwd
import os
import uuid
from services.common import resize_image
import logging
import json
import ast
from datetime import datetime

router = APIRouter()


@router.post("/category/", tags=["CATEGORY MANAGEMENT"])
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


@router.get("/category/", tags=["CATEGORY MANAGEMENT"])
def get_all(request: Request):
    return categoryService.get_all(request)


@router.get("/all-category/{page}", tags=["CATEGORY MANAGEMENT"])
def get_all_category(
    request: Request, page: int, show_page: int, search_query: Optional[str] = None
):
    return categoryService.get_all_category(request, page, show_page, search_query)


@router.get("/sub-category/{parent_id}", tags=["CATEGORY MANAGEMENT"])
def get_all_sub_category(request: Request, parent_id: int):
    return categoryService.get_all_sub_category(request, parent_id)


@router.get("/category-wise-product/{page}", tags=["CATEGORY MANAGEMENT"])
def get_category_wise_product(
    request: Request,
    page: int,
    identifier: str,
    show_page: int,
    sort_by: Optional[str] = None,
    price_range: Optional[str] = None,
    is_slug: bool = True,
):
    return categoryService.get_category_wise_product(
        request, page, identifier, show_page, sort_by, price_range, is_slug
    )


@router.get("/category/{parent_id}", tags=["CATEGORY MANAGEMENT"])
def get_category_by_parent_id(parent_id: int):
    return categoryService.get_category_by_parent_id(parent_id)


@router.put("/category/{category_id}", tags=["CATEGORY MANAGEMENT"])
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


@router.post("/category/change-status/{category_id}", tags=["CATEGORY MANAGEMENT"])
def change_category_status(category_id: str):
    return categoryService.change_category_status(category_id)


@router.delete("/category/{category_id}", tags=["CATEGORY MANAGEMENT"])
def delete_category(category_id: str):
    return categoryService.delete_category(category_id)
