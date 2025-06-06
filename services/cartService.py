from db import db
from .productService import get_product_by_id
from datetime import datetime
import services.shippingService as shippingService
import services.veracoreService as veracoreService
import services.taxService as taxService

collection = db["cart"]


def add_to_cart(user_id, products, updateStatus=False):
    try:
        # Convert any CartModel objects in products to dicts
        def to_dict(item):
            if hasattr(item, "dict"):
                return item.dict()
            elif hasattr(item, "__dict__"):
                return dict(item.__dict__)
            return item

        products_serialized = [to_dict(item) for item in products]

        cart_details = get_cart_by_user_id(user_id)

        if cart_details["status"] == "error":
            cart_data = {
                "customer_id": user_id,
                "products": products_serialized,
                "status": 1,
                "deleted_at": None,
                "created_by": user_id,
                "updated_by": None,
                "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "updated_at": None,
            }
            result = collection.insert_one(cart_data)
            return {
                "message": "data inserted successfully",
                "_id": str(result.inserted_id),
                "status": "success",
            }
        else:
            existing_products = cart_details["data"].get("products", [])
            # Merge logic: update quantity/varientArr if id matches, else append new
            updated_products = existing_products.copy()
            for new_item in products_serialized:
                found = False
                for idx, exist_item in enumerate(updated_products):
                    # if exist_item.get("id") == new_item.get("id") and exist_item.get("varientArr") == new_item.get("varientArr"):
                    if exist_item.get("id") == new_item.get("id"):
                        # Update quantity
                        updated_products[idx]["quantity"] = new_item.get("quantity", 0)
                        found = True
                        break
                if not found:
                    updated_products.append(new_item)

            # If status is True, remove products from DB cart that are not in the new products list
            update_data = {
                "products": products_serialized if updateStatus else updated_products,
                "updated_by": user_id,
                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }

            result = collection.update_one(
                {"customer_id": user_id}, {"$set": update_data}
            )
            if result.modified_count > 0:
                return {"message": "Cart updated successfully", "status": "success"}
            else:
                return {"message": "No changes made to the cart", "status": "info"}

    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_cart_details_by_product_id(product_id: str):
    try:
        result = collection.find({"product_id": product_id})
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_all_cart_details_by_user_id(request, user_id: str):
    try:
        cart_details = get_cart_by_user_id(user_id)
        if cart_details["status"] == "success" and cart_details["data"]:
            products = cart_details["data"].get("products", [])
            product_ids = [item["id"] for item in products] if products else []
            if len(product_ids) > 0:
                product_data = get_cart_details_by_product_arr(request, product_ids)
                if product_data["status"] == "success":
                    # Map server_cart_quantity, varientSuggestionArr, and varientArr from original cart products
                    for prod in product_data["data"]:
                        for cart_item in products:
                            if prod.get("_id") == cart_item.get("id"):
                                prod["cart_quantity"] = cart_item.get("quantity", 0)
                                prod["varientSuggestionArr"] = cart_item.get(
                                    "varientSuggestionArr", []
                                )
                                prod["varientArr"] = cart_item.get("varientArr", [])
                                break
                    cart_details["data"]["products"] = product_data["data"]
                    return {"data": cart_details["data"], "status": "success"}
                else:
                    return {
                        "message": "Error fetching product details",
                        "data": [],
                        "status": "error",
                    }
            else:
                return {
                    "message": "No products found in the cart",
                    "data": [],
                    "status": "error",
                }
        else:
            return {
                "message": "No cart found for this user",
                "data": [],
                "status": "error",
            }

    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_cart_by_user_id(customer_id: str):
    try:
        result = collection.find_one({"customer_id": customer_id})
        if result:
            result["_id"] = str(result["_id"])
            return {"data": result, "status": "success"}
        else:
            return {
                "message": "No cart found for this product and user",
                "status": "error",
            }
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_cart_details_by_product_id_user_id(product_id: str, user_id: str):
    try:
        result = collection.find({"product_id": product_id, "customer_id": user_id})
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_cart_details_by_product_arr(request, items):
    try:
        data = []
        shipping_company_name = ""

        AdminShipingDetails = shippingService.view_by_status(1)
        if (
            AdminShipingDetails["status"] == "success"
            and len(AdminShipingDetails["data"]) > 0
        ):
            shipping_company_name = AdminShipingDetails["data"][0][
                "shipping_company_name"
            ]

        for item in items:
            product_data = get_product_by_id(request, item)
            if product_data["data"] and len(product_data["data"]) > 0:
                if shipping_company_name == "Veracore":
                    veracoreproductdetails = (
                        veracoreService.get_veracore_product_details(
                            product_data["data"][0]["product_sku"]
                        )
                    )
                    if veracoreproductdetails["status"] == "success":
                        quantity = veracoreproductdetails["data"][0]["Available"]
                    else:
                        quantity = 0
                    product_data["data"][0]["quantity"] = quantity

                    data.append(product_data["data"][0])
                else:
                    data.append(product_data["data"][0])
        return {
            "data": data,
            "status": "success",
        }
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_shipping_and_tax_details(request):
    try:
        national_fix_amount: 0
        international_fix_amount: 0
        charges_above_national_fix_amount: 0
        charges_bellow_national_fix_amount: 0
        charges_above_international_fix_amount: 0
        charges_bellow_international_fix_amount: 0
        national_tax_percentage: 0
        international_tax_percentage: 0
        country_code: None

        AdminShipingDetails = shippingService.view_by_status(1)

        if (
            AdminShipingDetails["status"] == "success"
            and AdminShipingDetails["data"]
            and len(AdminShipingDetails["data"]) > 0
        ):
            national_fix_amount = AdminShipingDetails["data"][0]["national_fix_amount"]
            international_fix_amount = AdminShipingDetails["data"][0][
                "international_fix_amount"
            ]
            charges_above_national_fix_amount = AdminShipingDetails["data"][0][
                "charges_above_national_fix_amount"
            ]
            charges_bellow_national_fix_amount = AdminShipingDetails["data"][0][
                "charges_bellow_national_fix_amount"
            ]
            charges_above_international_fix_amount = AdminShipingDetails["data"][0][
                "charges_above_international_fix_amount"
            ]
            charges_bellow_international_fix_amount = AdminShipingDetails["data"][0][
                "charges_bellow_international_fix_amount"
            ]
            country_code = AdminShipingDetails["data"][0]["country_code"]

        AdminTaxDetails = taxService.viewTax()

        if (
            AdminTaxDetails["status"] == "success"
            and AdminTaxDetails["data"]
            and len(AdminTaxDetails["data"]) > 0
        ):
            national_tax_percentage = AdminTaxDetails["data"][0][
                "national_tax_percentage"
            ]
            international_tax_percentage = AdminTaxDetails["data"][0][
                "international_tax_percentage"
            ]
        return {
            "national_fix_amount": national_fix_amount,
            "international_fix_amount": international_fix_amount,
            "charges_above_national_fix_amount": charges_above_national_fix_amount,
            "charges_bellow_national_fix_amount": charges_bellow_national_fix_amount,
            "charges_above_international_fix_amount": charges_above_international_fix_amount,
            "charges_bellow_international_fix_amount": charges_bellow_international_fix_amount,
            "national_tax_percentage": national_tax_percentage,
            "international_tax_percentage": international_tax_percentage,
            "country_code": country_code,
            "status": "success",
        }
    except Exception as e:
        return {"message": str(e), "status": "error"}
