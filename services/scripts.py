import random
from db import db
from datetime import datetime, timedelta
import services.categoryService as categoryService
import re
from bson import ObjectId


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


def generate_dummy_order(product_ids, customer_id, addresses, random_date, statuses):
    status = random.choice(list(statuses.keys()))
    order_datetime = random_date(datetime(2023, 1, 1), datetime.now())

    order_at = order_datetime.strftime("%Y-%m-%d %H:%M:%S")
    order_date = order_datetime.strftime("%Y-%m-%d")
    order_time = order_datetime.strftime("%H:%M:%S")

    delivery_date = None
    # Set delivery_date if status is "order delivered" (6)
    if status == 6:
        delivery_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # Determine payment type based on status
    payment_type = "cash on delivery" if status in [2, 3, 4, 5, 6, 7] else "paypal"
    payment_method = "N/A" if payment_type == "cash on delivery" else "Online"
    transaction_id = (
        "N/A"
        if payment_type == "cash on delivery"
        else f"{random.randint(1000000000, 9999999999)}"
    )

    # Determine payment status and transaction status
    if payment_type == "paypal":
        payment_status = 1
        transaction_status = 1
        payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        payment_status_message = "COMPLETED"
    else:  # cash on delivery
        if status == 6:  # Order delivered
            payment_status = 1
            transaction_status = 1
            payment_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            payment_status_message = "COMPLETED"
        else:
            payment_status = 0
            transaction_status = 0
            payment_date = "N/A"
            payment_status_message = "payment pending"

    # Payment details for PayPal
    payment_details = (
        None
        if payment_type == "cash on delivery"
        else {
            "id": f"{random.randint(1000000000, 9999999999)}",
            "intent": "CAPTURE",
            "status": "COMPLETED",
            "purchase_units": [
                {
                    "reference_id": "default",
                    "amount": {
                        "currency_code": "USD",
                        "value": f"{random.uniform(1, 100):.2f}",
                    },
                    "payee": {
                        "email_address": "test@business.example.com",
                        "merchant_id": f"{random.randint(1000000, 9999999)}",
                    },
                    "soft_descriptor": "PAYPAL *TEST STORE",
                    "shipping": {
                        "name": {"full_name": "Test User"},
                        "address": {
                            "address_line_1": "Test Address",
                            "address_line_2": "Test Address Line 2",
                            "admin_area_2": "Test City",
                            "admin_area_1": "Test State",
                            "postal_code": "12345",
                            "country_code": "US",
                        },
                    },
                    "payments": {
                        "captures": [
                            {
                                "id": f"{random.randint(1000000000, 9999999999)}",
                                "status": "COMPLETED",
                                "amount": {
                                    "currency_code": "USD",
                                    "value": f"{random.uniform(1, 100):.2f}",
                                },
                                "final_capture": True,
                                "seller_protection": {"status": "NOT_ELIGIBLE"},
                                "create_time": datetime.now().isoformat(),
                                "update_time": datetime.now().isoformat(),
                            }
                        ]
                    },
                }
            ],
            "payer": {
                "name": {"given_name": "Test", "surname": "User"},
                "email_address": "test@example.com",
                "payer_id": f"{random.randint(1000000, 9999999)}",
                "address": {"country_code": "US"},
            },
            "create_time": datetime.now().isoformat(),
            "update_time": datetime.now().isoformat(),
            "links": [
                {
                    "href": "https://api.sandbox.paypal.com/v2/checkout/orders/12345",
                    "rel": "self",
                    "method": "GET",
                }
            ],
        }
    )

    order = {
        "order_details": {
            "total_quantity": 1,
            "varientArr": [random.randint(0, 2) for _ in range(2)],
            "total_price": random.randint(100, 1000),
            "discountInPercentage": 0,
            "discountedPrice": random.randint(100, 1000),
            "discountAmount": 0,
            "sale_price": random.randint(100, 1000),
            "varient_name_arr": ["Sample Variant"],
            "stock_quantity": random.randint(1, 50),
            "order_date": order_date,
            "order_cancel_status": None,
            "order_cancel_date": None,
            "order_cancel_amount": None,
            "shipped_date": None,
            "shipped_id": None,
            "delivery_date": delivery_date,
        },
        "payment_details": {
            "payment_type": payment_type,
            "payment_method": payment_method,
            "transaction_id": transaction_id,
            "transaction_status": transaction_status,
            "payment_status": payment_status,
            "payment_date": payment_date,
            "payment_status_message": payment_status_message,
            "payment_details": payment_details,
        },
        "product_id": random.choice(product_ids),
        "customer_id": customer_id,
        "address": random.choice(addresses),
        "bank_details": [],
        "order_tracking_id": random.randint(1, 100),
        "status": status,
        "deleted_at": None,
        "created_by": f"{random.randint(1000000, 9999999)}",
        "updated_by": None,
        "created_at": order_at,
        "created_date": order_date,
        "created_time": order_time,
        "updated_at": None,
    }

    return order


def generate_dummy_order_route_handle():
    product_ids = [
        "66c6e2cffc9c0596831e78c6",
        "66c6e2cffc9c0596831e78ae",
        "66c6e2cffc9c0596831e78b2",
        "66c6e2cffc9c0596831e78d1",
        "66c6e2cffc9c0596831e78e6",
        "66c6e2cffc9c0596831e78ba",
        "66c6e2cffc9c0596831e78c3",
        "66c6e2cffc9c0596831e78de",
        "66c6e2cffc9c0596831e78e8",
        "66c6e2cffc9c0596831e78bd",
    ]
    customer_id = "666c39bf25d367a583dd1e23"
    # Sample addresses
    addresses = [
        {
            "full_name": "Sonu",
            "phone_number": "9853192166",
            "country_id": 101,
            "state_id": 4013,
            "city_id": 131633,
            "pin_number": "754200",
            "roadName_area_colony": "Madhyakachha",
            "house_bulding_name": "NDUS-075",
            "landmark": "ME School",
            "primary_status": 1,
            "status": 1,
            "deleted_at": None,
            "id": 8,
        }
    ]

    # Helper function to generate random dates
    def random_date(start, end):
        return start + timedelta(
            seconds=random.randint(0, int((end - start).total_seconds()))
        )

    # Statuses
    statuses = {
        1: "order placed",
        2: "payment fail",
        3: "shipping fail",
        4: "quantity not available",
        5: "order shipped",
        6: "order delivered",
        7: " return request",
        8: "return request accepted",
        9: "refund initiated",
        10: "refund completed",
        11: " order cancelled ",
    }

    dummy_data = [
        generate_dummy_order(product_ids, customer_id, addresses, random_date, statuses)
        for _ in range(5000)
    ]

    db["order"].insert_many(dummy_data)
    return {"data": "data inserted successfully", "status": "success"}


def update_category_arr(parent_id, arr=None):
    if arr is None:
        arr = []

    collection = db["category"]
    result = collection.find_one({"id": parent_id})

    if result and "parent_id" in result:
        arr.append(result["parent_id"])
        update_category_arr(result["parent_id"], arr)

    return arr


def get_all_category_arr_hirarchy():
    collection = db["category"]
    result = collection.find()
    for item in result:
        parent_id_arr = update_category_arr(item["id"], None)
        # print("slug = > ",item['name'],type(item['_id']), update_category_arr(item['id'], None))
        collection.update_one(
            {"_id": item["_id"]}, {"$set": {"parent_id_arr": parent_id_arr}}
        )


def create_slug(input_string):
    # Convert to lowercase, remove unwanted characters, replace spaces/commas with hyphens
    slug = re.sub(
        r"[^a-z0-9\s,-]", "", input_string.lower()
    )  # Remove special characters except commas and hyphens
    slug = re.sub(r"[\s,]+", "-", slug)  # Replace spaces and commas with hyphens
    slug = re.sub(
        r"-+", "-", slug
    ).strip()  # Replace multiple hyphens with a single hyphen
    return slug


def convert_to_valid_slug():
    collection = db["product"]
    for (
        doc
    ) in (
        collection.find()
    ):  # Add filter if necessary, e.g., find({"slug": {"$exists": False}})
        original_value = doc.get(
            "slug", ""
        )  # Replace 'field_name' with your target field containing the input string
        if original_value:
            updated_slug = create_slug(original_value)
            # Update the document with the new slug
            collection.update_one({"_id": doc["_id"]}, {"$set": {"slug": updated_slug}})

    print("Slugs updated successfully.")


def generate_unique_slug(slug, existing_slugs):
    """
    Generates a unique slug by appending numbers to it.
    """
    if slug not in existing_slugs:
        return slug

    # Find the highest slug-number pattern like slug-1, slug-2, etc.
    max_number = 0
    slug_pattern = re.compile(f"^{re.escape(slug)}-(\\d+)$")
    for s in existing_slugs:
        match = slug_pattern.match(s)
        if match:
            max_number = max(max_number, int(match.group(1)))

    # Append the next number
    new_slug = f"{slug}-{max_number + 1}"
    return new_slug


def fix_duplicate_slugs():
    try:
        collection = db["product"]

        # Find all documents and store slugs
        all_docs = list(collection.find({}, {"slug": 1}))
        slug_count = {}

        for doc in all_docs:
            slug = doc["slug"]
            if slug in slug_count:
                slug_count[slug].append(doc["_id"])
            else:
                slug_count[slug] = [doc["_id"]]

        # Loop through each slug that has more than 1 occurrence
        for slug, ids in slug_count.items():
            if len(ids) > 1:
                # Find all existing slugs to avoid conflicts
                existing_slugs = [
                    doc["slug"]
                    for doc in collection.find({"slug": {"$regex": f"^{slug}-?"}})
                ]

                # Skip the first one (keep the original slug) and rename others
                for i, doc_id in enumerate(ids[1:], start=1):
                    new_slug = generate_unique_slug(slug, existing_slugs)
                    collection.update_one(
                        {"_id": ObjectId(doc_id)}, {"$set": {"slug": new_slug}}
                    )
                    existing_slugs.append(new_slug)

        return {"message": "Duplicate slugs fixed successfully"}

    except Exception as e:
        print(str(e))


def update_all_categories_parent_id_arr():
    documents = db["category"].find()
    updated_count = 0

    for document in documents:
        parent_id_arr = document.get("parent_id_arr", [])

        if parent_id_arr:
            sorted_parent_id_arr = sorted(parent_id_arr)
            update_result = db["category"].update_one(
                {"_id": document["_id"]},
                {"$set": {"parent_id_arr": sorted_parent_id_arr}},
            )
            if update_result.modified_count > 0:
                updated_count += 1

    if updated_count == 0:
        return {"detail": "No documents were updated"}

    return {"message": f"{updated_count} documents updated successfully"}


def update_sale_quantity_to_one():
    result = db["product"].update_many({}, {"$set": {"sold_quantity": 0}})
    return {"modified_count": result.modified_count}
