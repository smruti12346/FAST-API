from fastapi import Request
from db import db
from datetime import datetime
from bson import ObjectId
from services.common import paginate
from services.smtpService import send_email
import services.shippingService as shippingService
import services.productService as productService
import services.paymentService as paymentService
import services.taxService as taxService
import services.discountCouponService as discountCouponService
import services.userService as userService
import uuid
import time


collection = db["order"]


def update_variant_quantity(product, variant_arr, total_quantity, payment_id):
    current_variants = product["variant"]

    variant_names = []

    if len(current_variants) != 0 or len(variant_arr) != 0:
        # Traverse the variant structure to find the specified variant path
        for variant_index in variant_arr:
            if variant_index >= len(current_variants):
                return {
                    "message": "Variant not found.",
                    "payment_id": payment_id,
                    "status": "error",
                }

            current_variant = current_variants[variant_index]
            variant_names.append(current_variant["varient"])
            current_variants = current_variant.get("undervarient", [])

        # The final variant in the path
        final_variant = current_variant

        # Check if the final variant has enough quantity
        if final_variant["quantity"] < total_quantity:
            return {
                "message": f"Insufficient quantity for variant {final_variant['varient']}. Required: {total_quantity}, Available: {final_variant['quantity']}",
                "payment_id": payment_id,
                "status": "error",
            }

        # Update quantities along the variant path
        current_variants = product["variant"]
        for i, variant_index in enumerate(variant_arr):
            current_variant = current_variants[variant_index]
            current_variant["quantity"] -= total_quantity
            current_variants = current_variant.get("undervarient", [])

    product["quantity"] -= total_quantity
    return {"data": product, "status": "success"}


def check_order_quantity(product_id, varientArr):
    try:
        result = list(
            db["product"].find({"_id": ObjectId(product_id), "deleted_at": None})
        )
        updated_product = update_variant_quantity(result[0], varientArr, 2, "N/A")
        # print(updated_product)
        # return updated_product
    except Exception as e:
        return {"message": str(e), "status": "error"}


def check_order_quantity_by_order(product_details):
    try:
        if len(product_details) == 0:
            return {"message": "please choose product", "status": "error"}
        for existing_order in product_details:
            existing_order_data = existing_order.dict()
            result = list(
                db["product"].find(
                    {
                        "_id": ObjectId(existing_order_data["product_id"]),
                        "deleted_at": None,
                    }
                )
            )
            updated_product = update_variant_quantity(
                result[0],
                existing_order_data["order_details"]["varientArr"],
                existing_order_data["order_details"]["total_quantity"],
                "N/A",
            )

            if updated_product["status"] == "error":
                return updated_product

        return {"message": "Product available", "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_nested_variant(data, varientArr):
    current_variant = data
    for i, index in enumerate(varientArr):
        if i == 0:
            current_variant = current_variant[index]
        else:
            current_variant = current_variant["undervarient"][index]
    return current_variant


def get_percentage_value(total_price, percentage):
    return total_price * (percentage / 100)


def deduct_percentage(total_price, percentage):
    # Calculate the amount to add
    amount_to_add = total_price * (percentage / 100)
    # Calculate the new total price with the added percentage
    new_total_price = total_price - amount_to_add
    return new_total_price


def is_date_greater_than_today(date_str):
    given_date = datetime.strptime(date_str, "%d-%m-%Y")
    today = datetime.now().date()
    return given_date.date() > today


def claculate_data(
    product_id,
    total_quantity,
    varientArr,
    deliveryCharges,
    tax_percentage,
    discount_id,
    customer_id,
    payment_id,
):
    discount_in_percentage = 0
    if discount_id != "":
        response_data = discountCouponService.view_by_coupon_code_with_customer_id(
            discount_id, customer_id
        )

        if (
            response_data.get("status") == "success"
            and len(response_data.get("data", [])) > 0
        ):
            if is_date_greater_than_today(response_data["data"][0]["validity"]):
                discount_in_percentage = response_data["data"][0]["value_in_percentage"]
            else:
                discount_in_percentage = 0
        else:
            discount_in_percentage = 0

    product_detail = productService.get_product_by_id(Request, product_id)
    product_detail = (
        product_detail["data"][0] if product_detail["status"] == "success" else None
    )
    sale_price = float(product_detail["sale_price"])
    if len(varientArr) > 0:
        result = get_nested_variant(product_detail["variant"], varientArr)
        sale_price = float(result["price"])

    total_price_main = float(sale_price * total_quantity) + float(deliveryCharges)
    total_price_tax_value = round(
        get_percentage_value(total_price_main, tax_percentage), 2
    )
    total_price_discount_value = round(
        get_percentage_value(total_price_main, discount_in_percentage), 2
    )
    total_price = round(
        (total_price_main - total_price_discount_value) + total_price_tax_value, 2
    )

    return total_price


# def order_create(customer_id, country_code, product_details):
#     from services.userService import get_address_by_id

#     try:
#         # Initialize variables
#         orders, productQuntityArrs, paymetUnitsArr = [], [], []
#         (
#             total_price,
#             purchase_units_total_price,
#             fix_amount,
#             shipping_amount,
#             tax_percentage,
#         ) = (0, 0, 0, 0, 0)
#         order_models_dict_array = [order.dict() for order in product_details]
#         if len(order_models_dict_array) == 0:
#             return {"message": "please choose product", "status": "error"}

#         # Retrieve Payment Details
#         active_payment_details = paymentService.view_by_getway_name(
#             order_models_dict_array[0]["getway_name"]
#         )
#         if (
#             active_payment_details["status"] == "success"
#             and len(active_payment_details["data"]) > 0
#         ):
#             client_id = active_payment_details["data"][0]["api_key"]
#             secret_key = active_payment_details["data"][0]["password"]
#             currency_code = active_payment_details["data"][0]["currency"]
#             return_url = active_payment_details["data"][0]["return_url"]
#             cancel_url = active_payment_details["data"][0]["cancel_url"]
#         else:
#             return {
#                 "message": "There is some internal problem we unable to proceed your order, please try again later",
#                 "status": "error",
#             }

#         AdminTaxDetails = taxService.viewTax()

#         if (
#             AdminTaxDetails["status"] == "success"
#             and AdminTaxDetails["data"]
#             and len(AdminTaxDetails["data"]) > 0
#         ):
#             if AdminTaxDetails["data"][0]["country_code"] == country_code:
#                 tax_percentage = AdminTaxDetails["data"][0]["national_tax_percentage"]
#             else:
#                 tax_percentage = AdminTaxDetails["data"][0][
#                     "international_tax_percentage"
#                 ]

#         # Calculate Prices
#         for product_detail in order_models_dict_array:
#             total_price += float(
#                 claculate_data(
#                     product_detail["product_id"],
#                     product_detail["order_details"]["total_quantity"],
#                     product_detail["order_details"]["varientArr"],
#                     0,
#                     tax_percentage,
#                     product_detail["discount_id"],
#                     customer_id,
#                     product_detail["getway_name"],
#                 )
#             )

#         # print(total_price)
#         # Retrieve Shipping Details
#         AdminShipingDetails = shippingService.view_by_status(1)
#         if (
#             AdminShipingDetails["status"] == "success"
#             and len(AdminShipingDetails["data"]) > 0
#         ):
#             if AdminShipingDetails["data"][0]["country_code"] == country_code:
#                 fix_amount = AdminShipingDetails["data"][0]["national_fix_amount"]
#                 if total_price > fix_amount:
#                     shipping_amount = AdminShipingDetails["data"][0][
#                         "charges_above_national_fix_amount"
#                     ]
#                 else:
#                     shipping_amount = AdminShipingDetails["data"][0][
#                         "charges_bellow_national_fix_amount"
#                     ]
#             else:
#                 fix_amount = AdminShipingDetails["data"][0]["international_fix_amount"]
#                 if total_price > fix_amount:
#                     shipping_amount = AdminShipingDetails["data"][0][
#                         "charges_above_international_fix_amount"
#                     ]
#                 else:
#                     shipping_amount = AdminShipingDetails["data"][0][
#                         "charges_bellow_international_fix_amount"
#                     ]
#         else:
#             return {"message": "Shipping address not set", "status": "error"}

#         # Prepare Payment Units
#         for product_detail in order_models_dict_array:
#             purchase_units_total_price += float(
#                 claculate_data(
#                     product_detail["product_id"],
#                     product_detail["order_details"]["total_quantity"],
#                     product_detail["order_details"]["varientArr"],
#                     0,
#                     tax_percentage,
#                     product_detail["discount_id"],
#                     customer_id,
#                     product_detail["getway_name"],
#                 )
#             )

#             purchase_units = {
#                 "reference_id": str(uuid.uuid1()),
#                 "amount": {
#                     "value": total_price
#                     + (shipping_amount / len(order_models_dict_array)),
#                     "currency_code": currency_code,
#                 },
#             }
#             product_detail["order_details"]["deliveryCharges"] = shipping_amount / len(
#                 order_models_dict_array
#             )
#             product_detail["order_details"]["tax_percentage"] = tax_percentage
#             product_detail["order_details"]["total_price"] = (
#                 purchase_units_total_price
#                 + float(shipping_amount / len(order_models_dict_array))
#             )

#             product_detail["order_details"]["purchase_units"] = purchase_units
#             paymetUnitsArr.append(purchase_units)

#         # Generate Payment Link
#         paymentLinks = paymentService.create_paypal_order(
#             paymetUnitsArr, client_id, secret_key, return_url, cancel_url
#         )
#         paymentLinkGenerationStatus = (
#             "success" if "id" in paymentLinks["response"] else "error"
#         )
#         if paymentLinkGenerationStatus == "success":
#             for data in order_models_dict_array:
#                 data["payment_id"] = paymentLinks["response"]["id"]
#                 data["customer_id"] = customer_id
#                 address = get_address_by_id(data["customer_id"])
#                 if address["status"] == "success":
#                     primary_status_items = (
#                         [
#                             item
#                             for item in address["data"]
#                             if item["primary_status"] == 1
#                             and item.get("deleted_at") is None
#                             and item["status"] == 1
#                         ]
#                         if address.get("data")
#                         else []
#                     )
#                     if len(primary_status_items) == 0:
#                         return {
#                             "message": "Please enter your address",
#                             "status": "error",
#                         }
#                     data["address"] = primary_status_items[0]

#                 # Finalize Order Details
#                 data["created_by"] = data["customer_id"]
#                 data["order_details"]["order_date"] = str(
#                     datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#                 )
#                 data["order_details"]["order_cancel_status"] = None
#                 data["order_details"]["order_cancel_date"] = None
#                 data["order_details"]["order_cancel_amount"] = None
#                 data["order_details"]["shipped_date"] = None
#                 data["order_details"]["shipped_id"] = None
#                 data["order_details"]["delivery_date"] = None
#                 productQuntityArr = {
#                     "_id": data["product_id"],
#                     "total_quantity": data["order_details"]["total_quantity"],
#                 }
#                 productQuntityArrs.append(productQuntityArr)
#                 orders.append(data)

#             # Insert Orders and Return Payment Link
#             collection.insert_many(orders)
#             return paymentLinks
#         else:
#             return {
#                 "message": "Unable to generate payment link, please try again later",
#                 "status": "error",
#             }

#     except Exception as e:
#         return {"message": str(e), "status": "error"}


# def capture_created_order(cutomer_id, payment_id):
#     try:

#         results = list(collection.find({"payment_id": payment_id}))

#         if len(results) == 0:
#             return {
#                 "message": "Your order not found",
#                 "payment_id": payment_id,
#                 "status": "error",
#             }

#         for existing_order in results:
#             shp_id = existing_order["order_tracking_id"]
#             shp_rate_id = existing_order["order_details"]["shippingRateId"]
#             deliveryCharges = existing_order["order_details"]["deliveryCharges"]
#             getway_name = existing_order["getway_name"]

#         active_payment_details = paymentService.view_by_getway_name(getway_name)

#         if (
#             active_payment_details["status"] == "success"
#             and len(active_payment_details["data"]) > 0
#         ):
#             client_id = active_payment_details["data"][0]["api_key"]
#             secret_key = active_payment_details["data"][0]["password"]

#         # capture the payment start
#         paymentDetails = paymentService.capture_paypal_order(
#             payment_id, client_id, secret_key
#         )
#         if "id" not in paymentDetails["response"]:
#             return {
#                 "message": paymentDetails["response"]["details"][0]["description"],
#                 "payment_id": payment_id,
#                 "status": "error",
#             }
#         # capture the payment end

#         # buy shipment start
#         shippingDetails = shippingService.buy_shipment_for_deliver(
#             shp_id, shp_rate_id, deliveryCharges
#         )
#         if shippingDetails["status"] == "success":

#             filter = {"payment_id": payment_id}
#             update = {
#                 "$set": {
#                     "status": 3,
#                     "paymentDetails": paymentDetails,
#                     "shippingDetails": shippingDetails,
#                 }
#             }
#             collection.update_many(filter, update)
#         else:
#             filter = {"payment_id": payment_id}
#             update = {
#                 "$set": {
#                     "status": 2,
#                     "paymentDetails": paymentDetails,
#                     "shippingFailDetails": shippingDetails,
#                 }
#             }
#             collection.update_many(filter, update)

#         if shippingDetails["status"] == "error":
#             return {
#                 "message": "shipping failed! don't worry your money will be refunded",
#                 "payment_id": payment_id,
#                 "status": "error",
#             }
#         # buy shipment end

#         # check quantity start
#         for existing_order_data in results:
#             result = list(
#                 db["product"].find(
#                     {
#                         "_id": ObjectId(existing_order_data["product_id"]),
#                         "deleted_at": None,
#                     }
#                 )
#             )
#             updated_product = update_variant_quantity(
#                 result[0],
#                 existing_order_data["order_details"]["varientArr"],
#                 existing_order_data["order_details"]["total_quantity"],
#                 payment_id,
#             )

#             if updated_product["status"] == "error":
#                 return updated_product
#         # check quantity end

#         # update quantity and varient after check quantity
#         for existing_order_data in results:
#             result = list(
#                 db["product"].find(
#                     {
#                         "_id": ObjectId(existing_order_data["product_id"]),
#                         "deleted_at": None,
#                     }
#                 )
#             )
#             updated_product = update_variant_quantity(
#                 result[0],
#                 existing_order_data["order_details"]["varientArr"],
#                 existing_order_data["order_details"]["total_quantity"],
#                 payment_id,
#             )
#             db["product"].update_one(
#                 {"_id": ObjectId(existing_order_data["product_id"])},
#                 {
#                     "$set": {
#                         "quantity": int(updated_product["data"]["quantity"]),
#                         "variant": updated_product["data"]["variant"],
#                     },
#                     "$inc": {
#                         "sold_quantity": +existing_order_data["order_details"][
#                             "total_quantity"
#                         ]
#                     },
#                 },
#             )

#         filter = {"payment_id": payment_id}
#         update = {
#             "$set": {
#                 "status": 5,
#             }
#         }
#         collection.update_many(filter, update)
#         return {
#             "message": "Order placed successfully",
#             "payment_id": payment_id,
#             "status": "success",
#         }
#     except Exception as e:
#         return {"message": str(e), "payment_id": payment_id, "status": "error"}


def order_create(customer_details, country_code, product_details):
    from services.userService import get_address_by_id

    try:
        orders = []
        order_models_dict_array = [order.dict() for order in product_details]
        if len(order_models_dict_array) == 0:
            return {"message": "please choose product", "status": "error"}

        address = get_address_by_id(str(customer_details["_id"]))
        if address["status"] == "success":
            primary_status_items = (
                [
                    item
                    for item in address["data"]
                    if item["primary_status"] == 1
                    and item.get("deleted_at") is None
                    and item["status"] == 1
                ]
                if address.get("data")
                else []
            )
            if len(primary_status_items) == 0:
                return {
                    "message": "Please enter your address",
                    "status": "error",
                }

        for data in order_models_dict_array:
            data["address"] = primary_status_items[0]
            data["status"] = 1
            data["created_by"] = str(customer_details["_id"])
            data["customer_id"] = str(customer_details["_id"])
            data["order_details"]["order_date"] = str(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            orders.append(data)

        # Insert Orders and Return Payment Link
        collection.insert_many(orders)

        payment_id = order_models_dict_array[0]["payment_id"]

        # buy shipment start
        shippingDetails = shippingService.create_and_buy_shipment(customer_details, None)
        if shippingDetails["status"] == "success":
            shipping_id = shippingDetails["data"]["id"]
            filter = {"payment_id": payment_id}
            update = {
                "$set": {
                    "status": 3,
                    "shippingDetails": shippingDetails,
                    "order_tracking_id": shipping_id,
                }
            }
            collection.update_many(filter, update)
        else:
            shipping_id = shippingDetails["data"]["id"]
            filter = {"payment_id": payment_id}
            update = {
                "$set": {
                    "status": 2,
                    "shippingFailDetails": shippingDetails,
                    "order_tracking_id": shipping_id,
                }
            }
            collection.update_many(filter, update)

        if shippingDetails["status"] == "error":
            return {
                "message": "shipping failed! don't worry your money will be refunded",
                "payment_id": payment_id,
                "status": "error",
            }
        # buy shipment end

        # check quantity start
        for existing_order_data in order_models_dict_array:
            result = list(
                db["product"].find(
                    {
                        "_id": ObjectId(existing_order_data["product_id"]),
                        "deleted_at": None,
                    }
                )
            )
            updated_product = update_variant_quantity(
                result[0],
                existing_order_data["order_details"]["varientArr"],
                existing_order_data["order_details"]["total_quantity"],
                payment_id,
            )

            if updated_product["status"] == "error":
                return updated_product
        # check quantity end

        # # update quantity and varient after check quantity start
        # for existing_order_data in order_models_dict_array:
        #     result = list(
        #         db["product"].find(
        #             {
        #                 "_id": ObjectId(existing_order_data["product_id"]),
        #                 "deleted_at": None,
        #             }
        #         )
        #     )
        #     updated_product = update_variant_quantity(
        #         result[0],
        #         existing_order_data["order_details"]["varientArr"],
        #         existing_order_data["order_details"]["total_quantity"],
        #         payment_id,
        #     )
        #     db["product"].update_one(
        #         {"_id": ObjectId(existing_order_data["product_id"])},
        #         {
        #             "$set": {
        #                 "quantity": int(updated_product["data"]["quantity"]),
        #                 "variant": updated_product["data"]["variant"],
        #             },
        #             "$inc": {
        #                 "sold_quantity": +existing_order_data["order_details"][
        #                     "total_quantity"
        #                 ]
        #             },
        #         },
        #     )
        # # update quantity and varient after check quantity end

        filter = {"payment_id": payment_id}
        update = {
            "$set": {
                "status": 5,
            }
        }
        collection.update_many(filter, update)
        return {
            "message": "Order placed successfully",
            "payment_id": payment_id,
            "status": "success",
        }

    except Exception as e:
        return {"message": str(e), "status": "error"}


def guest_order_create(product_details):
    from services.userService import get_address_by_id
    from passlib.context import CryptContext

    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    try:
        orders = []
        order_models_dict_array = [order.dict() for order in product_details]
        if len(order_models_dict_array) == 0:
            return {"message": "please choose product", "status": "error"}

        user_details = userService.check_email_exist(
            order_models_dict_array[0]["address"]["email"]
        )

        address = order_models_dict_array[0]["address"]
        address["primary_status"] = 1
        address["status"] = 1
        address["deleted_at"] = None
        address["id"] = 1

        if user_details is None:
            user_data = {
                "email": order_models_dict_array[0]["address"]["email"],
                "name": order_models_dict_array[0]["address"]["full_name"],
                "mobile": order_models_dict_array[0]["address"]["phone_number"],
                "password": pwd_context.hash("user@123"),
                "dob": None,
                "gender": None,
                "profile_image": None,
                "address": [address],
                "bank_details": [],
                "user_type": 2,
                "user_permission": None,
                "description": None,
                "status": 1,
                "deleted_at": None,
                "created_at": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                "created_date": str(datetime.now().strftime("%Y-%m-%d")),
                "created_time": str(datetime.now().strftime("%H:%M:%S")),
                "created_by": None,
                "updated_at": None,
                "updated_by": None,
            }

            result = db["user"].insert_one(user_data)
            inserted_id = str(result.inserted_id)
        else:
            inserted_id = str(user_details["_id"])

        for data in order_models_dict_array:
            data["status"] = 1
            data["created_by"] = inserted_id
            data["customer_id"] = inserted_id
            data["order_details"]["order_date"] = str(
                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            )
            orders.append(data)
        # print(orders)

        # Insert Orders and Return Payment Link
        collection.insert_many(orders)

        payment_id = order_models_dict_array[0]["payment_id"]

        # buy shipment start
        shippingDetails = shippingService.create_and_buy_shipment(None, address)
        if shippingDetails["status"] == "success":
            shipping_id = shippingDetails["data"]["id"]
            filter = {"payment_id": payment_id}
            update = {
                "$set": {
                    "status": 3,
                    "shippingDetails": shippingDetails,
                    "order_tracking_id": shipping_id,
                }
            }
            collection.update_many(filter, update)
        else:
            shipping_id = shippingDetails["data"]["id"]
            filter = {"payment_id": payment_id}
            update = {
                "$set": {
                    "status": 2,
                    "shippingFailDetails": shippingDetails,
                    "order_tracking_id": shipping_id,
                }
            }
            collection.update_many(filter, update)

        if shippingDetails["status"] == "error":
            return {
                "message": "shipping failed! don't worry your money will be refunded",
                "payment_id": payment_id,
                "status": "error",
            }
        # buy shipment end

        # check quantity start
        for existing_order_data in order_models_dict_array:
            result = list(
                db["product"].find(
                    {
                        "_id": ObjectId(existing_order_data["product_id"]),
                        "deleted_at": None,
                    }
                )
            )
            updated_product = update_variant_quantity(
                result[0],
                existing_order_data["order_details"]["varientArr"],
                existing_order_data["order_details"]["total_quantity"],
                payment_id,
            )

            if updated_product["status"] == "error":
                return updated_product
        # check quantity end

        # update quantity and varient after check quantity start
        for existing_order_data in order_models_dict_array:
            result = list(
                db["product"].find(
                    {
                        "_id": ObjectId(existing_order_data["product_id"]),
                        "deleted_at": None,
                    }
                )
            )

            #  # check quantity avilable or not start
            # updated_product = update_variant_quantity(
            #     result[0],
            #     existing_order_data["order_details"]["varientArr"],
            #     existing_order_data["order_details"]["total_quantity"],
            #     payment_id,
            # )
            #  # check quantity avilable or not end

            db["product"].update_one(
                {"_id": ObjectId(existing_order_data["product_id"])},
                {
                    #  # impliment quantity start
                    # "$set": {
                    #     "quantity": int(updated_product["data"]["quantity"]),
                    #     "variant": updated_product["data"]["variant"],
                    # },
                    #  # impliment quantity end
                    "$inc": {
                        "sold_quantity": +existing_order_data["order_details"][
                            "total_quantity"
                        ]
                    },
                },
            )
        # update quantity and varient after check quantity end

        filter = {"payment_id": payment_id}
        update = {
            "$set": {
                "status": 5,
            }
        }
        collection.update_many(filter, update)
        return {
            "message": "Order placed successfully",
            "payment_id": payment_id,
            "status": "success",
        }

    except Exception as e:
        return {"message": str(e), "status": "error"}


def check_quantity(document):
    try:
        db_document = db["product"].find_one({"_id": ObjectId(document["_id"])})
        if db_document:
            return db_document["quantity"] >= document["total_quantity"]
        else:
            return False
    except Exception as e:
        print(f"An error occurred: {e}")
        return False


def update_quantity(document):
    try:
        db["product"].update_one(
            {"_id": ObjectId(document["_id"])},
            {
                "$inc": {
                    "quantity": -document["total_quantity"],
                    "sold_quantity": +document["total_quantity"],
                }
            },
        )
    except Exception as e:
        print(f"An error occurred: {e}")


def get_orders(request):
    try:
        pipeline = [
            {"$match": {}},
            {"$addFields": {"product_id_obj": {"$toObjectId": "$product_id"}}},
            {"$addFields": {"customer_id_obj": {"$toObjectId": "$customer_id"}}},
            {
                "$lookup": {
                    "from": "product",
                    "localField": "product_id_obj",
                    "foreignField": "_id",
                    "as": "product_details",
                }
            },
            {
                "$lookup": {
                    "from": "category",
                    "localField": "product_details.category_id",
                    "foreignField": "id",
                    "as": "category_details",
                }
            },
            {
                "$lookup": {
                    "from": "category",
                    "localField": "category_details.parent_id_arr",
                    "foreignField": "id",
                    "as": "parent_docs",
                }
            },
            {
                "$lookup": {
                    "from": "location",
                    "localField": "address.country_id",
                    "foreignField": "id",
                    "as": "parent_docs",
                }
            },
            {
                "$lookup": {
                    "from": "user",
                    "localField": "customer_id_obj",
                    "foreignField": "_id",
                    "as": "customer_details",
                }
            },
            {"$unwind": "$product_details"},
            {"$unwind": "$category_details"},
            {"$unwind": "$customer_details"},
            {
                "$addFields": {
                    "product_details.imageUrl": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/",
                            "$product_details.cover_image",
                        ]
                    },
                    "product_details.imageUrl100": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/100/",
                            "$product_details.cover_image",
                        ]
                    },
                    "product_details.imageUrl300": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/300/",
                            "$product_details.cover_image",
                        ]
                    },
                    "product_details.name": "$product_details.name",
                    "product_details.cover_image": "$product_details.cover_image",
                    "product_details.category_id": "$product_details.category_id",
                    "category_details.name": "$category_details.name",
                    "category_details.parent_id_arr": "$category_details.parent_id_arr",
                    "category_details.parent_arr": "$parent_docs.name",
                    "customer_details.name": "$customer_details.name",
                    "customer_details.email": "$customer_details.email",
                }
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "customer_id": 1,
                    "product_id": {"$toString": "$product_id"},
                    "order_details": 1,
                    "payment_details": 1,
                    "address": 1,
                    "bank_details": 1,
                    "order_tracking_id": 1,
                    "status": 1,
                    "product_details._id": {"$toString": "$product_details._id"},
                    "product_details.name": 1,
                    "product_details.cover_image": 1,
                    "product_details.imageUrl": 1,
                    "product_details.imageUrl100": 1,
                    "product_details.imageUrl300": 1,
                    "product_details.category_id": 1,
                    "category_details.name": 1,
                    "category_details.parent_arr": 1,
                    "customer_details.name": 1,
                    "customer_details.email": 1,
                }
            },
        ]
        result = list(collection.aggregate(pipeline))
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_all_orders(request, page, show_page):
    try:
        execution_start_time = time.time()
        pipeline = [
            {"$match": {}},
            {"$addFields": {"product_id_obj": {"$toObjectId": "$product_id"}}},
            {"$addFields": {"customer_id_obj": {"$toObjectId": "$customer_id"}}},
            {
                "$lookup": {
                    "from": "product",
                    "localField": "product_id_obj",
                    "foreignField": "_id",
                    "as": "product_details",
                }
            },
            {
                "$lookup": {
                    "from": "category",
                    "localField": "product_details.category_id",
                    "foreignField": "id",
                    "as": "category_details",
                }
            },
            {
                "$lookup": {
                    "from": "category",
                    "localField": "category_details.parent_id_arr",
                    "foreignField": "id",
                    "as": "parent_docs",
                }
            },
            {
                "$lookup": {
                    "from": "location",
                    "localField": "address.country_id",
                    "foreignField": "id",
                    "as": "parent_docs",
                }
            },
            {
                "$lookup": {
                    "from": "user",
                    "localField": "customer_id_obj",
                    "foreignField": "_id",
                    "as": "customer_details",
                }
            },
            {"$unwind": "$product_details"},
            {"$unwind": "$category_details"},
            {"$unwind": "$customer_details"},
            {
                "$addFields": {
                    "product_details.imageUrl": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/",
                            "$product_details.cover_image",
                        ]
                    },
                    "product_details.imageUrl100": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/100/",
                            "$product_details.cover_image",
                        ]
                    },
                    "product_details.imageUrl300": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/300/",
                            "$product_details.cover_image",
                        ]
                    },
                    "product_details.name": "$product_details.name",
                    "product_details.cover_image": "$product_details.cover_image",
                    "product_details.category_id": "$product_details.category_id",
                    "category_details.name": "$category_details.name",
                    "category_details.parent_id_arr": "$category_details.parent_id_arr",
                    "category_details.parent_arr": "$parent_docs.name",
                    "customer_details.name": "$customer_details.name",
                    "customer_details.email": "$customer_details.email",
                }
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "customer_id": 1,
                    "product_id": {"$toString": "$product_id"},
                    "order_details": 1,
                    "getway_name": 1,
                    "payment_details": 1,
                    "address": 1,
                    "bank_details": 1,
                    "order_tracking_id": 1,
                    "status": 1,
                    "product_details._id": {"$toString": "$product_details._id"},
                    "product_details.name": 1,
                    "product_details.cover_image": 1,
                    "product_details.imageUrl": 1,
                    "product_details.imageUrl100": 1,
                    "product_details.imageUrl300": 1,
                    "product_details.category_id": 1,
                    "category_details.name": 1,
                    "category_details.parent_arr": 1,
                    "customer_details.name": 1,
                    "customer_details.email": 1,
                }
            },
        ]

        # result = list(collection.aggregate(pipeline))
        result = paginate(collection, pipeline, page, show_page)
        return {
            "data": result,
            "status": "success",
            "duration": f"{time.time()-execution_start_time:.6f} seconds",
        }
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_orders_by_counts(request, page, show_page):
    try:
        pipeline = [
            {"$match": {}},
            {"$sort": {"created_at": -1}},
            {"$addFields": {"product_id_obj": {"$toObjectId": "$product_id"}}},
            {"$addFields": {"customer_id_obj": {"$toObjectId": "$customer_id"}}},
            {
                "$lookup": {
                    "from": "product",
                    "localField": "product_id_obj",
                    "foreignField": "_id",
                    "as": "product_details",
                }
            },
            {
                "$lookup": {
                    "from": "category",
                    "localField": "product_details.category_id",
                    "foreignField": "id",
                    "as": "category_details",
                }
            },
            {
                "$lookup": {
                    "from": "category",
                    "localField": "category_details.parent_id_arr",
                    "foreignField": "id",
                    "as": "parent_docs",
                }
            },
            {
                "$lookup": {
                    "from": "location",
                    "localField": "address.country_id",
                    "foreignField": "id",
                    "as": "parent_docs",
                }
            },
            {
                "$lookup": {
                    "from": "user",
                    "localField": "customer_id_obj",
                    "foreignField": "_id",
                    "as": "customer_details",
                }
            },
            {"$unwind": "$product_details"},
            {"$unwind": "$category_details"},
            {"$unwind": "$customer_details"},
            {
                "$addFields": {
                    "product_details.imageUrl": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/",
                            "$product_details.cover_image",
                        ]
                    },
                    "product_details.imageUrl100": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/100/",
                            "$product_details.cover_image",
                        ]
                    },
                    "product_details.imageUrl300": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/300/",
                            "$product_details.cover_image",
                        ]
                    },
                    "product_details.name": "$product_details.name",
                    "product_details.cover_image": "$product_details.cover_image",
                    "product_details.category_id": "$product_details.category_id",
                    "category_details.name": "$category_details.name",
                    "category_details.parent_id_arr": "$category_details.parent_id_arr",
                    "category_details.parent_arr": "$parent_docs.name",
                    "customer_details.name": "$customer_details.name",
                    "customer_details.email": "$customer_details.email",
                }
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "customer_id": 1,
                    "product_id": {"$toString": "$product_id"},
                    "order_details": 1,
                    "getway_name": 1,
                    "address": 1,
                    "bank_details": 1,
                    "order_tracking_id": 1,
                    "status": 1,
                    "product_details._id": {"$toString": "$product_details._id"},
                    "product_details.name": 1,
                    "product_details.cover_image": 1,
                    "product_details.imageUrl": 1,
                    "product_details.imageUrl100": 1,
                    "product_details.imageUrl300": 1,
                    "product_details.category_id": 1,
                    "category_details.name": 1,
                    "category_details.parent_arr": 1,
                    "customer_details.name": 1,
                    "customer_details.email": 1,
                    "created_at": 1,
                }
            },
            {"$limit": 5},
        ]
        documents = list(collection.aggregate(pipeline))
        return {"data": documents, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def find_variant(variants, variant_arr):
    current_variants = variants
    final_obj = {}
    variant_arr_name = []

    for variant_index in variant_arr:
        if variant_index >= len(current_variants):
            return None

        current_variant = current_variants[variant_index]
        variant_arr_name.append(current_variant["varient"])
        final_obj = current_variant
        current_variants = current_variant.get("undervarient", [])

    final_obj["VarientArrName"] = variant_arr_name
    return final_obj


def get_all_orders_by_user(request, user_id, page, show_page):
    try:
        check_order_tracking_status_and_update_user_wise_deliver_or_not(
            request, user_id
        )
        pipeline = [
            {"$match": {"customer_id": user_id}},
            {"$sort": {"created_at": -1}},
            {"$addFields": {"product_id_obj": {"$toObjectId": "$product_id"}}},
            {
                "$lookup": {
                    "from": "product",
                    "localField": "product_id_obj",
                    "foreignField": "_id",
                    "as": "product_details",
                }
            },
            {
                "$lookup": {
                    "from": "location",
                    "localField": "address.country_code",
                    "foreignField": "iso2",
                    "as": "country_details",
                }
            },
            {"$unwind": "$country_details"},
            {"$unwind": "$country_details.states"},
            {
                "$match": {
                    "$expr": {
                        "$eq": [
                            "$country_details.states.state_code",
                            "$address.state_code",
                        ]
                    }
                }
            },
            {"$unwind": "$country_details.states.cities"},
            {
                "$match": {
                    "$expr": {
                        "$eq": [
                            "$country_details.states.cities.name",
                            "$address.city_name",
                        ]
                    }
                }
            },
            {"$unwind": "$product_details"},
            {
                "$addFields": {
                    "product_details.imageUrl100": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/100/",
                            "$product_details.cover_image",
                        ]
                    },
                    "product_details.name": "$product_details.name",
                    "product_details.slug": "$product_details.slug",
                    # "address.country_name": "$country_details.name",
                    # "address.state_name": "$country_details.states.name",
                    # "address.city_name": "$country_details.states.cities.name",
                }
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "customer_id": 1,
                    "product_id": {"$toString": "$product_id"},
                    "order_details": 1,
                    "payment_details": 1,
                    "shippingDetails": 1,
                    "address": 1,
                    "bank_details": 1,
                    "order_tracking_id": 1,
                    "status": 1,
                    "product_details._id": {"$toString": "$product_details._id"},
                    "product_details.name": 1,
                    "product_details.slug": 1,
                    "product_details.imageUrl100": 1,
                    "created_at": 1,
                }
            },
        ]

        result = paginate(collection, pipeline, page, show_page)
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_order_details_by_order_id(request, order_id):
    try:

        # print(order_id)
        pipeline = [
            {"$match": {"_id": ObjectId(order_id)}},
            {"$addFields": {"product_id_obj": {"$toObjectId": "$product_id"}}},
            {"$addFields": {"customer_id_obj": {"$toObjectId": "$customer_id"}}},
            {
                "$lookup": {
                    "from": "product",
                    "localField": "product_id_obj",
                    "foreignField": "_id",
                    "as": "product_details",
                }
            },
            {
                "$lookup": {
                    "from": "user",
                    "localField": "customer_id_obj",
                    "foreignField": "_id",
                    "as": "user_details",
                }
            },
            {
                "$lookup": {
                    "from": "location",
                    "localField": "address.country_code",
                    "foreignField": "iso2",
                    "as": "country_details",
                }
            },
            {"$unwind": "$country_details"},
            {"$unwind": "$country_details.states"},
            {
                "$match": {
                    "$expr": {
                        "$eq": [
                            "$country_details.states.state_code",
                            "$address.state_code",
                        ]
                    }
                }
            },
            {"$unwind": "$country_details.states.cities"},
            {
                "$match": {
                    "$expr": {
                        "$eq": [
                            "$country_details.states.cities.name",
                            "$address.city_name",
                        ]
                    }
                }
            },
            {"$unwind": "$product_details"},
            {"$unwind": "$user_details"},
            {
                "$addFields": {
                    "product_details.name": "$product_details.name",
                    "product_details.slug": "$product_details.slug",
                    "product_details.main_price": "$product_details.main_price",
                    "product_details.description": "$product_details.description",
                    "address.country_name": "$country_details.name",
                    "address.state_name": "$country_details.states.name",
                    "address.city_name": "$country_details.states.cities.name",
                    "user_details.email": "$user_details.email",
                    "user_details.name": "$user_details.name",
                    "user_details.mobile": "$user_details.mobile",
                    "user_details.profile_image": "$user_details.profile_image",
                    "product_details.imageUrl": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/",
                            "$product_details.cover_image",
                        ]
                    },
                }
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "discount_id": 1,
                    "customer_id": 1,
                    "product_id": {"$toString": "$product_id"},
                    "order_details": 1,
                    "payment_details": 1,
                    "address": 1,
                    "bank_details": 1,
                    "order_tracking_id": 1,
                    "status": 1,
                    "product_details._id": {"$toString": "$product_details._id"},
                    "product_details.name": 1,
                    "product_details.slug": 1,
                    "product_details.main_price": 1,
                    "product_details.sale_price": 1,
                    "product_details.description": 1,
                    "product_details.imageUrl": 1,
                    "user_details.email": 1,
                    "user_details.name": 1,
                    "user_details.mobile": 1,
                    "user_details.profile_image": 1,
                    "payment_id": 1,
                    "getway_name": 1,
                    "created_at": 1,
                }
            },
        ]
        result = list(collection.aggregate(pipeline))
        if len(result) > 0:
            shipping_details = shippingService.get_shipping_label(
                result[0]["order_tracking_id"]
            )
            if shipping_details["status"] != "error":
                result[0]["shipping_details"] = shipping_details["data"]
            else:
                result[0]["shipping_details"] = {}

        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def update_payment_status(order_id):
    try:
        result = collection.update_one(
            {"_id": ObjectId(order_id)},
            {
                "$set": {
                    "payment_details.payment_method": "Offline",
                    "payment_details.payment_status": 1,
                    "payment_details.transaction_status": 1,
                    "payment_details.payment_status": 1,
                    "payment_details.payment_date": str(
                        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    ),
                    "payment_details.payment_status_message": "COMPLETED",
                }
            },
        )
        if result.modified_count == 1:
            return {"message": "Payment successfully", "status": "success"}
        else:
            return {"message": "failed to payment", "status": "error"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def update_order_status(order_id, status, customer_id, user_type):
    try:
        if user_type != 1:
            db_document = collection.find_one(
                {"_id": ObjectId(order_id), "customer_id": customer_id}
            )
            if db_document == None:
                return {"message": "Please Login First", "status": "error"}

        result = collection.update_one(
            {"_id": ObjectId(order_id)},
            {
                "$set": {
                    "status": status,
                    "updated_at": str(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                }
            },
        )
        if result.modified_count == 1:
            return {"message": "status updated successfully", "status": "success"}
        else:
            return {"message": "failed update status", "status": "error"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_all_orders_status_wise(request, statusArr, page, show_page):
    try:
        pipeline = [
            {"$match": {"status": {"$in": statusArr}}},
            {"$addFields": {"product_id_obj": {"$toObjectId": "$product_id"}}},
            {"$addFields": {"customer_id_obj": {"$toObjectId": "$customer_id"}}},
            {
                "$lookup": {
                    "from": "product",
                    "localField": "product_id_obj",
                    "foreignField": "_id",
                    "as": "product_details",
                }
            },
            {
                "$lookup": {
                    "from": "category",
                    "localField": "product_details.category_id",
                    "foreignField": "id",
                    "as": "category_details",
                }
            },
            {
                "$lookup": {
                    "from": "category",
                    "localField": "category_details.parent_id_arr",
                    "foreignField": "id",
                    "as": "parent_docs",
                }
            },
            {
                "$lookup": {
                    "from": "location",
                    "localField": "address.country_id",
                    "foreignField": "id",
                    "as": "parent_docs",
                }
            },
            {
                "$lookup": {
                    "from": "user",
                    "localField": "customer_id_obj",
                    "foreignField": "_id",
                    "as": "customer_details",
                }
            },
            {"$unwind": "$product_details"},
            {"$unwind": "$category_details"},
            {"$unwind": "$customer_details"},
            {
                "$addFields": {
                    "product_details.imageUrl": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/",
                            "$product_details.cover_image",
                        ]
                    },
                    "product_details.imageUrl100": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/100/",
                            "$product_details.cover_image",
                        ]
                    },
                    "product_details.imageUrl300": {
                        "$concat": [
                            str(request.base_url)[:-1],
                            "/uploads/products/300/",
                            "$product_details.cover_image",
                        ]
                    },
                    "product_details.name": "$product_details.name",
                    "product_details.cover_image": "$product_details.cover_image",
                    "product_details.category_id": "$product_details.category_id",
                    "category_details.name": "$category_details.name",
                    "category_details.parent_id_arr": "$category_details.parent_id_arr",
                    "category_details.parent_arr": "$parent_docs.name",
                    "customer_details.name": "$customer_details.name",
                    "customer_details.email": "$customer_details.email",
                }
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "customer_id": 1,
                    "product_id": {"$toString": "$product_id"},
                    "order_details": 1,
                    "getway_name": 1,
                    "payment_details": 1,
                    "address": 1,
                    "bank_details": 1,
                    "order_tracking_id": 1,
                    "status": 1,
                    "product_details._id": {"$toString": "$product_details._id"},
                    "product_details.name": 1,
                    "product_details.cover_image": 1,
                    "product_details.imageUrl": 1,
                    "product_details.imageUrl100": 1,
                    "product_details.imageUrl300": 1,
                    "product_details.category_id": 1,
                    "category_details.name": 1,
                    "category_details.parent_arr": 1,
                    "customer_details.name": 1,
                    "customer_details.email": 1,
                    "created_at": 1,
                }
            },
        ]

        # result = list(collection.aggregate(pipeline))
        result = paginate(collection, pipeline, page, show_page)
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_all_orders_count_status_wise():
    try:
        pipeline = [
            {
                "$group": {
                    "_id": "$status",
                    "count": {"$sum": 1},
                }
            }
        ]

        result = list(collection.aggregate(pipeline))
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_order_invoice(request, data, background_tasks):
    try:
        data = dict(data)
        results = get_order_details_by_order_id(request, data["order_id"])

        if results["status"] == "success" and results["data"][0]:
            result = results["data"][0]
            if result["status"] == 4 or result["status"] == 5 or result["status"] == 6:
                # print(result)
                body = f"""
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Invoice</title>
                        <style>
                            body {{
                                font-family: 'Arial', sans-serif;
                                margin: 0;
                                padding: 0;
                                background-color: #f5f5f5;
                            }}
                            
                            .invoice-box {{
                                max-width: 800px;
                                margin: 20px auto;
                                padding: 30px;
                                border: 1px solid #eee;
                                background-color: #fff;
                            }}
                            
                            table {{
                                width: 100%;
                                line-height: inherit;
                                text-align: left;
                                border-collapse: collapse;
                            }}
                            
                            table td {{
                                padding: 8px;
                                vertical-align: top;
                            }}
                            
                            table tr.top table td {{
                                padding-bottom: 20px;
                            }}
                            
                            table tr.top table td.title {{
                                font-size: 45px;
                                line-height: 45px;
                                color: #333;
                            }}
                            
                            table tr.information table td {{
                                padding-bottom: 40px;
                            }}
                            
                            table tr.heading td {{
                                background: #eee;
                                border-bottom: 1px solid #ddd;
                                font-weight: bold;
                                text-align: right;
                            }}
                            
                            table tr.item td {{
                                border-bottom: 1px solid #eee;
                                text-align: right;
                            }}
                            
                            table tr.item.last td {{
                                border-bottom: none;
                            }}
                            
                            table tr.total td:nth-child(2) {{
                                border-top: 2px solid #eee;
                                font-weight: bold;
                                padding-top: 10px;
                                padding-bottom: 10px;
                            }}
                            
                            .terms {{
                                margin-top: 40px;
                                font-size: 14px;
                            }}
                            
                            h2, p {{
                                margin: 0;
                            }}
                            
                            h2 {{
                                font-size: 22px;
                            }}
                            
                            .title p {{
                                font-size: 14px;
                                line-height: 1.5;
                            }}
                            
                            .top td, .information td, .heading td, .item td, .total td {{
                                font-size: 14px;
                            }}
                            
                            .left {{
                                float: left;
                                width: 60%;
                            }}
                            
                            .right {{
                                float: right;
                                width: 40%;
                                text-align: right;
                            }}
                            
                            .clearfix {{
                                overflow: auto;
                            }}
                        </style>
                    </head>
                    <body>
                        <div class="invoice-box">
                            <table>
                                <tr class="top">
                                    <td colspan="5">
                                        <div class="clearfix">
                                            <div class="left">
                                                <h2>Zylker Electronics Hub</h2>
                                                <p>14B, Northern Street Greater South Avenue<br>
                                                New York New York 10001 U.S.A</p>
                                            </div>
                                            <div class="right">
                                                <p>INVOICE</p>
                                                <p>Invoice# : {result.get('_id', '')}<br>
                                                Order Date : {result.get('created_at', '')}<br>
                                                Terms : Due on Receipt<br>
                                                Due Date : {result.get('created_at', '')}</p>
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                                <tr class="information">
                                    <td colspan="5">
                                        <div class="clearfix">
                                            <div class="left">
                                                <p>Bill To</p>
                                                <p>{result.get('user_details')['name']}<br>
                                                {result.get('address')['country_name']}<br>
                                                {result.get('address')['state_name']}<br>
                                                {result.get('address')['city_name']}, {result.get('address')['pin_number']}</p>
                                            </div>
                                            <div class="right">
                                                <p>Ship To</p>
                                                <p>{result.get('address')['full_name']}<br>
                                                {result.get('address')['country_name']}<br>
                                                {result.get('address')['state_name']}<br>
                                                {result.get('address')['city_name']}, {result.get('address')['pin_number']}, near {result.get('address')['landmark']}</p>
                                            </div>
                                        </div>
                                    </td>
                                </tr>
                                <tr class="heading">
                                    <td>#</td>
                                    <td>Item & Description</td>
                                    <td>Qty</td>
                                    <td>Rate</td>
                                    <td>Amount</td>
                                </tr>
                                <!-- Example of dynamic item list -->
                                
                                <tr class="item">
                                    <td>1</td>
                                    <td>{result.get('product_details')['name']}</td>
                                    <td>{result.get('order_details')['total_quantity']}</td>
                                    <td>{result.get('product_details')['main_price']}</td>
                                    <td>{result.get('order_details')['sale_price']}</td>
                                </tr>
                                <tr class="total">
                                    <td colspan="4" style="text-align: right;">Sub Total</td>
                                    <td style="text-align: right;">{result.get('order_details')['sale_price']}</td>
                                </tr>
                                <tr class="total">
                                    <td colspan="4" style="text-align: right;">Discount</td>
                                    <td style="text-align: right;">{result.get('order_details')['discountAmount']} ( {result.get('order_details')['discountInPercentage']}% )</td>
                                </tr>
                                <tr class="total">
                                    <td colspan="4" style="text-align: right;">Balance Due</td>
                                    <td style="text-align: right;">{result.get('order_details')['total_price']}</td>
                                </tr>
                            </table>
                            <p class="terms">Thanks for shopping with us.</p>
                            <p class="terms">Terms & Conditions<br>
                            Full payment is due upon receipt of this invoice.<br>
                            Late payments may incur additional charges or interest as per the applicable laws.</p>
                        </div>
                    </body>
                    </html>
                    """
                # print(body)
                background_tasks.add_task(
                    send_email,
                    result.get("user_details")["email"],
                    "Invoice Report",
                    body,
                )
                return {"message": "Email sent successfully", "status": "success"}
            else:
                return {"message": "Unable to generate invoice", "status": "error"}
        else:
            return {"message": "No data found", "status": "error"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_order_details_by_id(request, order_id):
    try:
        result = list(collection.find({"_id": ObjectId(order_id), "deleted_at": None}))
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def check_order_tracking_status_and_update_deliver_or_not(request):
    try:
        results = list(collection.find({"status": 5, "deleted_at": None}))
        for result in results:
            trk_id = result["shippingDetails"]["data"]["tracker"]["id"]
            trk_details = shippingService.track_order_by_id(trk_id)
            # print(trk_details)
            if trk_details["status"] == "success":
                if trk_details["data"]["status"] == "delivered":
                    collection.update_one(
                        {"_id": ObjectId(result["_id"])}, {"$set": {"status": 6}}
                    )
        return {"data": "success", "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def check_order_tracking_status_and_update_user_wise_deliver_or_not(
    request, customer_id
):
    try:
        results = list(
            collection.find(
                {"status": 5, "customer_id": customer_id, "deleted_at": None}
            )
        )
        for result in results:
            trk_id = result["shippingDetails"]["data"]["tracker"]["id"]
            trk_details = shippingService.track_order_by_id(trk_id)
            if trk_details["status"] == "success":
                if trk_details["data"]["status"] == "delivered":
                    collection.update_one(
                        {"_id": ObjectId(result["_id"])}, {"$set": {"status": 6}}
                    )
        return {"data": "success", "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def create_order_return_request(request, order_id):
    try:
        orderData = get_order_details_by_id(request, order_id)
        if orderData["status"] == "success" and len(orderData["data"]) > 0:
            shippingData = orderData["data"][0]["shippingDetails"]

            if shippingData["status"] == "success" and len(shippingData["data"]) > 0:
                buyer_address = shippingData["data"]["buyer_address"]["id"]
                from_address = shippingData["data"]["from_address"]["id"]
                parcel_id = shippingData["data"]["parcel"]["id"]

                payment_id = orderData["data"][0]["payment_id"]
                reference_id = orderData["data"][0]["order_details"]["purchase_units"][
                    "reference_id"
                ]

                active_payment_details = paymentService.view_by_getway_name(
                    orderData["data"][0]["getway_name"]
                )

                if (
                    active_payment_details["status"] == "success"
                    and len(active_payment_details["data"]) > 0
                ):
                    client_id = active_payment_details["data"][0]["api_key"]
                    secret_key = active_payment_details["data"][0]["password"]

                payment_refund_details = paymentService.refund_paypal_payment(
                    payment_id, reference_id, client_id, secret_key
                )
                if payment_refund_details["status"] == "error":
                    return {
                        "data": payment_refund_details["message"],
                        "status": "error",
                    }

                shipment = shippingService.create_return_request(
                    buyer_address, from_address, parcel_id
                )

                if shipment["status"] == "error":
                    return {
                        "data": shipment["message"],
                        "status": "error",
                    }

                db["order"].update_one(
                    {"_id": ObjectId(order_id)},
                    {
                        "$set": {
                            # "status": 6,
                            "status": 10,
                            "return_request_details": shipment,
                            "payment_refund_details": payment_refund_details,
                            "updated_at": str(
                                datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            ),
                        }
                    },
                )
                return {
                    "data": "return request accepted successfully",
                    "status": "success",
                }

            else:
                return {"message": "Shipping details not found", "status": "error"}
        else:
            return {"message": "Order details not found", "status": "error"}
    except Exception as e:
        return {"message": str(e), "status": "error"}
