import easypost
import json
import services.locationService as locationService
from services import orderService
from services import veracoreService
from services import easyPostShippingService
from db import db
from bson import ObjectId
from datetime import datetime
from .common import paginate
import uuid

import requests

import services.paymentService as paymentService

api_key = "2TDp15wsUbcC95Z42Y4BrQ"
client = easypost.EasyPostClient(api_key)

collection = db["shipping"]


def create(data, id):
    try:
        data = dict(data)
        if (
            collection.count_documents({"api_key": data["api_key"], "deleted_at": None})
            != 0
        ):
            return {"message": "API key already exist", "status": "error"}

        data["id"] = (
            int(dict(collection.find_one({}, sort=[("id", -1)]))["id"]) + 1
            if collection.find_one({}, sort=[("id", -1)]) is not None
            else 1
        )
        data["admin_id"] = id
        result = collection.insert_one(data)
        return {
            "message": "data inserted successfully",
            "_id": str(result.inserted_id),
            "status": "success",
        }
    except Exception as e:
        return {"message": str(e), "status": "error"}


def view(request, page, show_page):
    try:
        pipeline = [
            {"$match": {"deleted_at": None}},
            {"$addFields": {"admin_id_obj": {"$toObjectId": "$admin_id"}}},
            {
                "$lookup": {
                    "from": "user",
                    "localField": "admin_id_obj",
                    "foreignField": "_id",
                    "as": "UserDetails",
                }
            },
            {"$unwind": "$UserDetails"},
            {
                "$addFields": {
                    "addressDetails": {
                        "$filter": {
                            "input": "$UserDetails.address",
                            "as": "address",
                            "cond": {"$eq": ["$$address.id", "$address_id"]},
                        },
                    },
                    "user_name": "$UserDetails.name",
                    "user_email": "$UserDetails.email",
                    "user_mobile": "$UserDetails.mobile",
                }
            },
            {"$unwind": "$addressDetails"},
            {
                "$lookup": {
                    "from": "location",
                    "localField": "country_code",
                    "foreignField": "iso2",
                    "as": "addressDetailsForCurrencyAndCountryName",
                }
            },
            {"$unwind": "$addressDetailsForCurrencyAndCountryName"},
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "id": 1,
                    "name": 1,
                    "shipping_company_name": 1,
                    "domain_url": 1,
                    "currency": 1,
                    "national_fix_amount": 1,
                    "charges_above_national_fix_amount": 1,
                    "charges_bellow_national_fix_amount": 1,
                    "international_fix_amount": 1,
                    "charges_above_international_fix_amount": 1,
                    "charges_bellow_international_fix_amount": 1,
                    "address_id": 1,
                    "user_id": 1,
                    "admin_id": 1,
                    "password": 1,
                    "api_key": 1,
                    "owner_id": 1,
                    "status": 1,
                    "created_at": 1,
                    "addressDetails": 1,
                    "user_name": 1,
                    "user_email": 1,
                    "user_mobile": 1,
                    "country_code": 1,
                    "addressDetailsForCurrencyAndCountryName.name": 1,
                    "addressDetailsForCurrencyAndCountryName.iso2": 1,
                }
            },
        ]

        result = paginate(collection, pipeline, page, show_page)

        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def view_by_id(id):
    try:
        result = list(collection.find({"_id": ObjectId(id), "deleted_at": None}))
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def view_by_status(status):
    try:
        pipeline = [
            {"$match": {"status": status, "deleted_at": None}},
            {"$addFields": {"admin_id_obj": {"$toObjectId": "$admin_id"}}},
            {
                "$lookup": {
                    "from": "user",
                    "localField": "admin_id_obj",
                    "foreignField": "_id",
                    "as": "UserDetails",
                }
            },
            {"$unwind": "$UserDetails"},
            {
                "$addFields": {
                    "addressDetails": {
                        "$filter": {
                            "input": "$UserDetails.address",
                            "as": "address",
                            "cond": {"$eq": ["$$address.id", "$address_id"]},
                        },
                    },
                    "user_name": "$UserDetails.name",
                    "user_email": "$UserDetails.email",
                    "user_mobile": "$UserDetails.mobile",
                }
            },
            {"$unwind": "$addressDetails"},
            {
                "$lookup": {
                    "from": "location",
                    "localField": "country_code",
                    "foreignField": "iso2",
                    "as": "addressDetailsForCurrencyAndCountryName",
                }
            },
            {"$unwind": "$addressDetailsForCurrencyAndCountryName"},
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "id": 1,
                    "name": 1,
                    "shipping_company_name": 1,
                    "domain_url": 1,
                    "currency": 1,
                    "country_code": 1,
                    "national_fix_amount": 1,
                    "charges_above_national_fix_amount": 1,
                    "charges_bellow_national_fix_amount": 1,
                    "international_fix_amount": 1,
                    "charges_above_international_fix_amount": 1,
                    "charges_bellow_international_fix_amount": 1,
                    "address_id": 1,
                    "user_id": 1,
                    "admin_id": 1,
                    "password": 1,
                    "api_key": 1,
                    "status": 1,
                    "created_at": 1,
                    "addressDetails": 1,
                    "user_name": 1,
                    "user_email": 1,
                    "user_mobile": 1,
                    "addressDetailsForCurrencyAndCountryName.name": 1,
                    "addressDetailsForCurrencyAndCountryName.iso2": 1,
                }
            },
        ]
        result = collection.aggregate(pipeline)
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def view_by_shipping_company_name(shipping_company_name):
    try:
        pipeline = [
            {"$match": {"shipping_company_name": shipping_company_name, "deleted_at": None}},
            {"$addFields": {"admin_id_obj": {"$toObjectId": "$admin_id"}}},
            {
                "$lookup": {
                    "from": "user",
                    "localField": "admin_id_obj",
                    "foreignField": "_id",
                    "as": "UserDetails",
                }
            },
            {"$unwind": "$UserDetails"},
            {
                "$addFields": {
                    "addressDetails": {
                        "$filter": {
                            "input": "$UserDetails.address",
                            "as": "address",
                            "cond": {"$eq": ["$$address.id", "$address_id"]},
                        },
                    },
                    "user_name": "$UserDetails.name",
                    "user_email": "$UserDetails.email",
                    "user_mobile": "$UserDetails.mobile",
                }
            },
            {"$unwind": "$addressDetails"},
            {
                "$lookup": {
                    "from": "location",
                    "localField": "country_code",
                    "foreignField": "iso2",
                    "as": "addressDetailsForCurrencyAndCountryName",
                }
            },
            {"$unwind": "$addressDetailsForCurrencyAndCountryName"},
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "id": 1,
                    "name": 1,
                    "shipping_company_name": 1,
                    "domain_url": 1,
                    "currency": 1,
                    "country_code": 1,
                    "national_fix_amount": 1,
                    "charges_above_national_fix_amount": 1,
                    "charges_bellow_national_fix_amount": 1,
                    "international_fix_amount": 1,
                    "charges_above_international_fix_amount": 1,
                    "charges_bellow_international_fix_amount": 1,
                    "address_id": 1,
                    "user_id": 1,
                    "admin_id": 1,
                    "password": 1,
                    "api_key": 1,
                    "status": 1,
                    "created_at": 1,
                    "addressDetails": 1,
                    "user_name": 1,
                    "user_email": 1,
                    "user_mobile": 1,
                    "addressDetailsForCurrencyAndCountryName.name": 1,
                    "addressDetailsForCurrencyAndCountryName.iso2": 1,
                }
            },
        ]
        result = collection.aggregate(pipeline)
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}


        # result = list(
        #     collection.find(
        #         {
        #             "shipping_company_name": shipping_company_name,
        #             "status": 1,
        #             "deleted_at": None,
        #         }
        #     )
        # )
        # data = []
        # for doc in result:
        #     doc["_id"] = str(doc["_id"])
        #     data.append(doc)
        # return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def view_by_getway_name(getway_name):
    try:
        result = list(
            collection.find(
                {"getway_name": getway_name, "status": 1, "deleted_at": None}
            )
        )
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def update(id, data):
    try:
        data = dict(data)
        result = collection.update_one({"_id": ObjectId(id)}, {"$set": data})
        if result.modified_count == 1:
            return {"message": "data updated successfully", "status": "success"}
        else:
            return {"message": "failed to update", "status": "error"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def delete(payment_id: str):
    result = collection.update_one(
        {"_id": ObjectId(payment_id)},
        {"$set": {"deleted_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}},
    )
    if result.modified_count == 1:
        return {"message": "data deleted successfully", "status": "success"}
    else:
        return {"message": "failed to delete", "status": "error"}


def change_status(payment_id: str):
    getStatus = view_by_id(payment_id)["data"][0]["status"]

    if getStatus == 0:
        collection.update_many({}, {"$set": {"status": 0}})
        status = 1
    else:
        status = 0

    result = collection.update_one(
        {"_id": ObjectId(payment_id)},
        {"$set": {"status": status}},
    )
    if result.modified_count == 1:
        return {"message": "status changed successfully", "status": "success"}
    else:
        return {"message": "failed to change status", "status": "error"}


# ====================================================================================================
# ====================================================================================================
# ====================================================================================================


def validate_address(street1, city, state, zip, country, email, phone):

    try:
        AdminShipingDetails = view_by_status(1)
        if (
            AdminShipingDetails["status"] == "success"
            and len(AdminShipingDetails["data"]) > 0
        ):
            shipping_company_name = AdminShipingDetails["data"][0][
                "shipping_company_name"
            ]
            api_key = AdminShipingDetails["data"][0]["api_key"]
        else:
            return {"message": "Shipping address not set", "status": "error"}

        if shipping_company_name == "self":
            return {
                "data": {
                    "verifications": {"delivery": {"success": True}},
                    "shipping_company_name": "self",
                },
                "status": "success",
            }

        if shipping_company_name == "Veracore":
            return {
                "data": {
                    "verifications": {"delivery": {"success": True}},
                    "shipping_company_name": "Veracore",
                },
                "status": "success",
            }

        client = easypost.EasyPostClient(api_key)
        address = client.address.create(
            verify_strict=True,
            street1=street1,  # "Bapuji Nagar Lane No 5 67",
            city=city,  # "Bhubaneswar",
            state=state,  # "OD",
            zip=zip,  # "751009",
            country=country,  # "IN",
            email=email,  # "test@example.com",
            phone=phone,  # "5555555555",
        )
        return {"data": json.loads(json.dumps(address.to_dict())), "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def create_shipment_and_get_rates(data, userAddressDetails=None, productDetails=None):
    try:

        if userAddressDetails is None:
            for item in data["address"]:
                if item["primary_status"] == 1:
                    userAddressDetails = item

        AdminShipingDetails = view_by_status(1)
        if (
            AdminShipingDetails["status"] == "success"
            and len(AdminShipingDetails["data"]) > 0
        ):
            shipping_company_name = AdminShipingDetails["data"][0][
                "shipping_company_name"
            ]
            api_key = AdminShipingDetails["data"][0]["api_key"]
        else:
            return {"message": "Shipping address not set", "status": "error"}

        if shipping_company_name == "self":
            return {
                "data": {
                    "id": str(uuid.uuid1()),
                    "shipping_company_name": "self",
                    "tracker": None,
                },
                "shipping_company_response": None,
                "status": "success",
            }

        if shipping_company_name == "Veracore":
            if userAddressDetails is not None:
                # print(productDetails)

                user_address = {
                    "Prefix": None,
                    "FirstName": userAddressDetails["full_name"],
                    "LastName": "",
                    "Address1": userAddressDetails["roadName_area_colony"],
                    "City": userAddressDetails["city_name"],
                    "State": userAddressDetails["state_code"],
                    "PostalCode": userAddressDetails["pin_number"],
                    "Country": userAddressDetails["country_code"],
                    "Phone": userAddressDetails["phone_number"],
                    "Email": None,
                }

                productsresult = list(
                    db["product"].find(
                        {
                            "_id": ObjectId(productDetails[0]["product_id"]),
                            "deleted_at": None,
                        }
                    )
                )

                shipment = veracoreService.veracore_order_fulfill(
                    productsresult[0]["product_sku"],
                    productDetails[0]["order_details"]["total_quantity"],
                    productDetails[0]["order_details"]["sale_price"],
                    user_address,
                )
                return {
                    "data": {
                        "id": shipment["OrderID"],
                        "shipping_company_name": "Veracore",
                        "tracker": None,
                    },
                    "shipping_company_response": shipment,
                    "status": "success",
                }
            else:
                return {"message": "Please select address", "status": "error"}

        if shipping_company_name == "EasyPostUps":
            # client = easypost.EasyPostClient(api_key)
            productsresult = list(
                db["product"].find(
                    {
                        "_id": ObjectId(productDetails[0]["product_id"]),
                        "deleted_at": None,
                    }
                )
            )

            parcel = {
                "length": float(productsresult[0].get("length", 20.2)),
                "width": float(productsresult[0].get("width", 10.9)),
                "height": float(productsresult[0].get("height", 5)),
                "weight": float(productsresult[0].get("weight", 65.9)),
            }

            if userAddressDetails is not None:
                shipment = easyPostShippingService.easypost_order_fulfill(
                    data, userAddressDetails, AdminShipingDetails, api_key, parcel
                )

                return {
                    "data": {
                        "id": shipment['data']["id"],
                        "shipping_company_name": "EasyPostUps",
                        "tracker": None,
                    },
                    "shipping_company_response": shipment['data'],
                    "status": shipment['status'],
                }

            else:
                return {"message": "Please select address", "status": "error"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_created_shipment_details(shp_id: str):
    try:
        AdminShipingDetails = view_by_status(1)
        if (
            AdminShipingDetails["status"] == "success"
            and len(AdminShipingDetails["data"]) > 0
        ):
            api_key = AdminShipingDetails["data"][0]["api_key"]
        else:
            return {"message": "Shipping address not set", "status": "error"}

        client = easypost.EasyPostClient(api_key)
        retrieved_shipment = client.shipment.retrieve(shp_id)

        return {"data": retrieved_shipment, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def refund_shipment_before_deliver(shipping_id: str):
    try:
        shipment = client.shipment.refund(shipping_id)
        return {"data": json.loads(json.dumps(shipment.to_dict())), "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def track_order_by_id(trk_id):
    try:
        tracker = client.tracker.retrieve(trk_id)
        return {"data": json.loads(json.dumps(tracker.to_dict())), "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


# def create_return_request(buyer_address, from_address, parcel_id):
#     try:
#         AdminShipingDetails = view_by_status(1)
#         if (
#             AdminShipingDetails["status"] == "success"
#             and len(AdminShipingDetails["data"]) > 0
#         ):
#             api_key = AdminShipingDetails["data"][0]["api_key"]
#         else:
#             return {"message": "Shipping address not set", "status": "error"}

#         client = easypost.EasyPostClient(api_key)
#         shipment = client.shipment.create(
#             to_address={"id": buyer_address},
#             from_address={"id": from_address},
#             parcel={"id": parcel_id},
#             is_return=True,
#         )


#         return {
#             "message": json.loads(json.dumps(shipment.to_dict())),
#             "status": "success",
#         }
#     except Exception as e:
#         return {"message": str(e), "status": "error"}
def create_return_request(request, order_id):
    try:

        orderData = orderService.get_order_details_by_id(request, order_id)
        if orderData["status"] == "success" and len(orderData["data"]) > 0:
            shippingData = orderData["data"][0]["shippingDetails"]

            if (
                shippingData["status"] == "success"
                and shippingData["data"]["shipping_company_name"]
                and shippingData["data"]["shipping_company_name"] == "self"
            ):
                AdminShipingDetails = view_by_status(1)
                if (
                    AdminShipingDetails["status"] == "success"
                    and len(AdminShipingDetails["data"]) > 0
                ):
                    address_id = AdminShipingDetails["data"][0]["address_id"]
                    pipeline = [
                        {
                            "$match": {"user_type": 1, "address.id": address_id}
                        },  # Match documents with address id = 1
                        {
                            "$project": {
                                "address": {
                                    "$filter": {
                                        "input": "$address",
                                        "as": "addr",
                                        "cond": {
                                            "$eq": ["$$addr.id", address_id]
                                        },  # Filter for address with id = 1
                                    }
                                }
                            }
                        },
                    ]
                    result = list(db["user"].aggregate(pipeline))
                    if result:
                        from_address = result
                    else:
                        return {"message": "No admin address found", "status": "error"}
                else:
                    return {"message": "Shipping address not set", "status": "error"}
                return {
                    "message": {
                        "buyer_address": orderData["data"][0]["address"],
                        "from_address": from_address,
                    },
                    "status": "success",
                }

            if shippingData["status"] == "success" and len(shippingData["data"]) > 0:
                buyer_address = shippingData["data"]["buyer_address"]["id"]
                from_address = shippingData["data"]["from_address"]["id"]
                parcel_id = shippingData["data"]["parcel"]["id"]

                AdminShipingDetails = view_by_status(1)
                if (
                    AdminShipingDetails["status"] == "success"
                    and len(AdminShipingDetails["data"]) > 0
                ):
                    api_key = AdminShipingDetails["data"][0]["api_key"]
                else:
                    return {"message": "Shipping address not set", "status": "error"}

                client = easypost.EasyPostClient(api_key)
                shipment = client.shipment.create(
                    to_address={"id": buyer_address},
                    from_address={"id": from_address},
                    parcel={"id": parcel_id},
                    is_return=True,
                )

                return {
                    "message": json.loads(json.dumps(shipment.to_dict())),
                    "status": "success",
                }
            else:
                return {
                    "message": "Shipping details not found for this order",
                    "status": "error",
                }
        else:
            return {"message": "Order not found", "status": "error"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def check_return_status(request, shipping_id):
    try:
        shipment = client.shipment.retrieve(shipping_id)
        return {
            "message": json.loads(json.dumps(shipment.to_dict())),
            "status": "success",
        }

    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_shipping_label(shipping_id):
    try:
        result = {}
        shipment = client.shipment.label(shipping_id, file_format="PDF")
        shipping_details = json.loads(json.dumps(shipment.to_dict()))
        result["postage_label_url"] = shipping_details["postage_label"]["label_url"]
        result["billing_type"] = shipping_details["selected_rate"]["billing_type"]
        result["carrier"] = shipping_details["selected_rate"]["carrier"]
        result["carrier_account_id"] = shipping_details["selected_rate"][
            "carrier_account_id"
        ]
        result["currency"] = shipping_details["selected_rate"]["retail_currency"]
        result["retail_rate"] = shipping_details["selected_rate"]["retail_rate"]
        result["tracking_url"] = shipping_details["tracker"]["public_url"]

        return {
            "data": result,
            "status": "success",
        }
    except Exception as e:
        return {"message": str(e), "status": "error"}


def create_and_buy_shipment(data, userAddressdetails, productDetails):
    created_shipment = create_shipment_and_get_rates(
        data, userAddressdetails, productDetails
    )
    # print(created_shipment)

    if created_shipment["status"] == "success":
        shipping_company_name = created_shipment["data"].get("shipping_company_name")

        if shipping_company_name and shipping_company_name == "self":
            return created_shipment

        if shipping_company_name and shipping_company_name == "Veracore":
            return created_shipment

        if shipping_company_name and shipping_company_name == "EasyPostUps":
            easypost_buy_shipment =  easyPostShippingService.buy_shipment_for_deliver(created_shipment["data"]["id"], 0, 0)
            if easypost_buy_shipment['status'] == "success":
                created_shipment['shipping_company_response'] = easypost_buy_shipment['data']
                created_shipment['data']['tracker'] = easypost_buy_shipment['data']['tracker']['public_url']
                return created_shipment
            else:
                return easypost_buy_shipment            

    else:
        return {"message": "unable to create shipment", "status": "error"}


def get_address_using_zip_code(zip_code):
    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {"address": zip_code, "key": api_key}

    response = requests.get(url, params=params)

    if response.status_code == 200:
        data = response.json()
        if data["status"] == "OK" and data["results"]:
            return data["results"][0]["formatted_address"]
        else:
            print("No address found for the specified ZIP code.")
    else:
        print("Error retrieving address:", response.text)
