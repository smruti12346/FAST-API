from fastapi import APIRouter, UploadFile, File, Body, Request, Query
import services.productService as productService
from services.common import resize_image
from Models.Products import ProductModel, VariantItem
import services.scripts as scripts
from typing import List
import os
import uuid
from os import getcwd
import json
import logging


router = APIRouter()


@router.get("/search_products/")
def search_products(query: str = Query(...)):
    return productService.search_products(query)


@router.get("/products/")
def get_all(request: Request):
    return productService.get_all(request)


@router.get("/products/{product_id}")
def get_product_by_id(request: Request, product_id: str):
    return productService.get_product_by_id(request, product_id)


@router.get("/products_by_slug/{product_slug}")
def get_product_by_slug(request: Request, product_slug: str):
    return productService.get_product_by_slug(request, product_slug)


@router.post("/products/")
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


@router.put("/products/{product_id}")
def update_product(product_id: str, product_data: ProductModel):
    return productService.update(product_id, product_data)


@router.put("/update_product_variant/{product_id}")
def update_product_variant(product_id: str, VariantItem: List[VariantItem]):
    return productService.update_product_variant(product_id, VariantItem)


@router.put("/update_only_product_quantity/{product_id}")
def update_only_product_quantity(product_id: str, total_quantity: int):
    return productService.update_only_product_quantity(product_id, total_quantity)


@router.delete("/products/{product_id}")
def delete_product(product_id: str):
    return productService.delete_product(product_id)

