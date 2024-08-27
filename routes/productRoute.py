from fastapi import APIRouter, UploadFile, File, Body, Request, Query, Depends
import services.productService as productService
from services.common import resize_image
from Models.Products import ProductModel, VariantItem, ProductUpdateModel
from typing import List, Optional
import os
import uuid
from os import getcwd
import json
import logging
import services.userService as userService


router = APIRouter()


# ======================================================================================================
# ======================================================================================================
# ======================================================================================================
@router.post("/products/", tags=["PRODUCT MANAGEMENT"])
async def create_product(
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
        return {"error": "An error occurred while creating product."}


# @router.get("/products/", tags=["PRODUCT MANAGEMENT"])
# def get_all(request: Request):
#     return productService.get_all(request)


@router.get("/all-products/{page}", tags=["PRODUCT MANAGEMENT"])
def get_all_product(request: Request, page: int, show_page: int):
    return productService.get_all_product(request, page, show_page)


@router.put("/products/{product_id}", tags=["PRODUCT MANAGEMENT"])
async def update_product(
    product_id: str,
    product_data: ProductUpdateModel,
    cover_image: Optional[UploadFile] = File(None),
    images: Optional[List[UploadFile]] = File(None)
):

    try:
        PATH_FILES = getcwd() + "/uploads/products/"
        os.makedirs(PATH_FILES, exist_ok=True)

        if cover_image :
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
            product_data.cover_image = cover_image_filename + ".webp"

        if images :
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

            product_data.images = additional_image_filenames
        

        if product_data.seo is not None:
            product_data.seo = json.loads(product_data.seo)
        if product_data.variant is not None:
            product_data.variant = json.loads(product_data.variant)

        return productService.update(product_id, product_data)
    except Exception as e:
        return {"error": "An error occurred while creating product."}


@router.delete("/products/{product_id}", tags=["PRODUCT MANAGEMENT"])
def delete_product(product_id: str):
    return productService.delete_product(product_id)


@router.get("/products/{product_id}", tags=["PRODUCT FILTER"])
def get_product_by_id(request: Request, product_id: str):
    return productService.get_product_by_id(request, product_id)


@router.get("/products_by_slug/{product_slug}", tags=["PRODUCT FILTER"])
def get_product_by_slug(request: Request, product_slug: str):
    return productService.get_product_by_slug(request, product_slug)


@router.get("/search_products/", tags=["PRODUCT FILTER"])
def search_products(query: str = Query(...)):
    return productService.search_products(query)


# ======================================================================================================
# ======================================================================================================
# ======================================================================================================
@router.put(
    "/update_product_variant/{product_id}",
    tags=["PRODUCT VARIENT / QUANTITY MANAGEMENT"],
)
def update_product_variant(product_id: str, VariantItem: List[VariantItem]):
    return productService.update_product_variant(product_id, VariantItem)


@router.put(
    "/update_only_product_quantity/{product_id}",
    tags=["PRODUCT VARIENT / QUANTITY MANAGEMENT"],
)
def update_only_product_quantity(product_id: str, total_quantity: int):
    return productService.update_only_product_quantity(product_id, total_quantity)


# ======================================================================================================
# ======================================================================================================
# ======================================================================================================
@router.post("/create-review", tags=["PRODUCT REVIEW MANAGEMENT"])
async def create_review(
    product_id: str,
    point: int,
    review: str,
    review_image: UploadFile = File(...),
    token: str = Depends(userService.get_current_user),
):
    if "_id" in token:
        return await productService.create_review(
            product_id, point, review, review_image, token
        )
    else:
        return await {"message": "Not authenticated", "status": "error"}


@router.get("/get-product-wise-review/{product_id}", tags=["PRODUCT REVIEW MANAGEMENT"])
def get_product_wise_review(product_id: str):
    return productService.get_product_wise_review(product_id)


@router.get("/get-products-wise-reviews/{page}/", tags=["PRODUCT REVIEW MANAGEMENT"])
def get_products_wise_reviews(request: Request, page: int, show_page: int):
    return productService.get_products_wise_reviews(request, page, show_page)


@router.get("/get-product-review/{product_id}", tags=["PRODUCT REVIEW MANAGEMENT"])
def get_product_review(product_id: str):
    return productService.get_product_review(product_id)
