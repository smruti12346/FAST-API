import random
import uuid
import json
from datetime import datetime
from db import db
import random
from datetime import datetime, timedelta


def random_date(start, end):
    start_u = start.timestamp()
    end_u = end.timestamp()
    random_u = random.uniform(start_u, end_u)
    return datetime.fromtimestamp(random_u)


def generate_dummy_categorys(num_categories):
    categories = []
    for i in range(1, num_categories + 1):
        category = {
            "parent_id": 0,
            "parent_id_arr": [0],
            "name": f"Category {i}",
            "slug": f"category-{i}",
            "image": f"uploads\\category\\image-{i}.jpg",
            "description": "test",
            "variant": None,
            "seo": {
                "meta_title": "test",
                "meta_description": "test",
                "meta_fields": "test",
            },
            "status": 1,
            "deleted_at": None,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "created_by": None,
            "updated_at": None,
            "updated_by": None,
            "id": i,
        }
        categories.append(category)

        # Adding subcategories
        num_subcategories = random.randint(1, 3)  # Random number of subcategories
        for j in range(1, num_subcategories + 1):
            subcategory = {
                "parent_id": i,
                "parent_id_arr": [i],
                "name": f"Subcategory {j} of Category {i}",
                "slug": f"subcategory-{j}-of-category-{i}",
                "image": f"uploads\\category\\subcategory-image-{j}-of-category-{i}.jpg",
                "description": "test",
                "variant": None,
                "seo": {
                    "meta_title": "test",
                    "meta_description": "test",
                    "meta_fields": "test",
                },
                "status": 1,
                "deleted_at": None,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "created_by": None,
                "updated_at": None,
                "updated_by": None,
                "id": len(categories) + j,
            }
            categories.append(subcategory)
    return categories


def get_categories_from_db():
    categories = db["category"].find({})
    return list(categories)


# Generate random dummy product data
def generate_dummy_products(n):
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)

    products = []
    for i in range(n):
        sale_price = random.randint(500, 1000)
        random_datetime = random_date(start_date, end_date)
        formatted_random_datetime = random_datetime.strftime("%Y-%m-%d %H:%M:%S")
        category = random.choice([5, 6, 7, 8, 9, 10, 11])
        product = {
            "id": i + 1,
            "name": f"Product {i+1}",
            "category_id": int(category),
            "slug": f"product-{i+1}",
            "cover_image": "e0b38842-1838-11ef-80a5-d2acf1736445-1.webp",  # Random cover image name
            "images": [
                f"e0b38842-1838-11ef-80a5-d2acf1736445-1.webp" for j in range(1, 7)
            ],  # Random image names
            "description": f"Description for product {i+1}",
            "main_price": random.randint(1000, 2000),
            "sale_price": sale_price,  # Adjusted to be lower than main_price
            "currency": "INDIAN",
            "quantity": 90,
            "sold_quantity": random.randint(0, 200),
            "shipping_status": random.choice([None, "shipped", "pending"]),
            "shipping_value": None,
            "variant": [
                {
                    "varientname": "parent",
                    "varient": "color",
                    "quantity": 90,
                    "price": sale_price,
                    "undervarient": [
                        {
                            "varientname": "color",
                            "varient": "red",
                            "quantity": 50,
                            "price": sale_price,
                            "undervarient": [
                                {
                                    "varientname": "red",
                                    "varient": "xl",
                                    "quantity": 30,
                                    "price": sale_price,
                                    "undervarient": [],
                                },
                                {
                                    "varientname": "red",
                                    "varient": "xxl",
                                    "quantity": 20,
                                    "price": sale_price,
                                    "undervarient": [],
                                },
                            ],
                        },
                        {
                            "varientname": "color",
                            "varient": "blue",
                            "quantity": 40,
                            "price": sale_price,
                            "undervarient": [
                                {
                                    "varientname": "blue",
                                    "varient": "xl",
                                    "quantity": 15,
                                    "price": sale_price,
                                    "undervarient": [],
                                },
                                {
                                    "varientname": "blue",
                                    "varient": "xxl",
                                    "quantity": 25,
                                    "price": sale_price,
                                    "undervarient": [],
                                },
                            ],
                        },
                    ],
                }
            ],
            "status": 1,
            "deleted_at": None,
            "created_at": str(formatted_random_datetime),
        }
        products.append(product)
    return products


def generate_dummy_product():
    n = 200
    dummy_products = generate_dummy_products(n)
    # return {"data": dummy_products, "status": "success"}

    db["product"].insert_many(dummy_products)
    return {"data": "data inserted successfully", "status": "success"}
