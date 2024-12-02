from db import db
from services import shippingService
import easypost
import requests
import json

collection = db["shipping"]


def validate_address(street1, city, state, zip, country, email, phone):

    try:
        AdminShipingDetails = shippingService.view_by_status(1)
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


def easypost_order_fulfill(
    data, userAddressDetails, AdminShipingDetails, api_key, parcel
):
    try:
        client = easypost.EasyPostClient(api_key)

        shipment = client.shipment.create(
            # carrier_accounts=["ca_c42e6d3b0c3c4964ae880ce2f0e62588"],
            # service="Express",
            to_address={
                "name": userAddressDetails["full_name"],  # "Dr. Steve Brule",
                "street1": userAddressDetails[
                    "roadName_area_colony"
                ],  # "179 N Harbor Dr",
                "city": userAddressDetails["city_name"],  # "Redondo Beach",
                "state": userAddressDetails["state_code"],  # "CA",
                "zip": userAddressDetails["pin_number"],  # "90277",
                "country": userAddressDetails["country_code"],  # "US",
                "phone": userAddressDetails["phone_number"],  # "4153334444",
                "email": (
                    data["email"] if data != None else userAddressDetails["email"]
                ),  # "dr_steve_brule@gmail.com",
            },
            from_address={
                "name": AdminShipingDetails["data"][0]["name"],  # "EasyPost"
                "street1": AdminShipingDetails["data"][0]["addressDetails"][
                    "roadName_area_colony"
                ],  # "417 Montgomery Street",
                "street2": AdminShipingDetails["data"][0]["addressDetails"][
                    "house_bulding_name"
                ],  # "5th Floor",
                "city": AdminShipingDetails["data"][0]["addressDetails"][
                    "city_name"
                ],  # "San Francisco",
                "state": AdminShipingDetails["data"][0]["addressDetails"][
                    "state_code"
                ],  # "CA",
                "zip": AdminShipingDetails["data"][0]["addressDetails"][
                    "pin_number"
                ],  # "94104",
                "country": AdminShipingDetails["data"][0]["addressDetails"][
                    "country_code"
                ],  # "US",
                "phone": AdminShipingDetails["data"][0]["user_mobile"],  # "4153334444",
                "email": AdminShipingDetails["data"][0][
                    "user_email"
                ],  # "support@easypost.com",
            },
            # parcel={
            #     "length": 20.2,
            #     "width": 10.9,
            #     "height": 5,
            #     "weight": 65.9,
            # },
            parcel=parcel,
        )
        return {
            "data": json.loads(json.dumps(shipment.to_dict())),
            "status": "success",
        }

    except Exception as e:
        return {"message": str(e), "status": "error"}


def buy_shipment_for_deliver(shp_id: str, rates_index: int, deliveryCharges: int):
    try:
        AdminShipingDetails = shippingService.view_by_status(1)
        if (
            AdminShipingDetails["status"] == "success"
            and len(AdminShipingDetails["data"]) > 0
        ):
            api_key = AdminShipingDetails["data"][0]["api_key"]
        else:
            return {"message": "Shipping address not set", "status": "error"}

        client = easypost.EasyPostClient(api_key)

        retrieved_shipment = client.shipment.retrieve(shp_id)
        # if deliveryCharges == 0:
        #     final_rate = retrieved_shipment.lowest_rate()
        # else:
        #     final_rate = retrieved_shipment.rates[rates_index]

        final_rate = retrieved_shipment.lowest_rate()
        shipment = client.shipment.buy(
            retrieved_shipment.id,
            rate=final_rate,
            # insurance=249.99,
        )
        return {"data": json.loads(json.dumps(shipment.to_dict())), "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}
