import easypost
import json
import services.locationService as locationService
from services import orderService
from db import db
from bson import ObjectId
from datetime import datetime

api_key = "2TDp15wsUbcC95Z42Y4BrQ"
client = easypost.EasyPostClient(api_key)


def validate_address(street1, city, state, zip, country, email, phone):

    try:
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


# def create_shipment_and_get_rates(name, street1, city_id, state_id, zip, country_id, email, phone):
def create_shipment_and_get_rates(data):
    try:
        # print(data)

        userAddressDetails = ""

        for item in data["address"]:
            if item["primary_status"] == 1:
                userAddressDetails = item

        if userAddressDetails != "":

            country_details = locationService.get_country_by_id(
                userAddressDetails["country_id"]
            )["data"]
            state_details = locationService.get_states_by_state_id_and_country_id(
                userAddressDetails["country_id"], userAddressDetails["state_id"]
            )["data"]
            city_details = locationService.get_city_by_city_id_country_id_and_state_id(
                userAddressDetails["country_id"],
                userAddressDetails["state_id"],
                userAddressDetails["city_id"],
            )["data"]

            if country_details and len(country_details) > 0:
                country = country_details[0]["iso2"]
            else:
                return {"message": "Country not found", "status": "error"}

            if state_details and len(state_details) > 0:
                state = state_details[0]["state_code"]
            else:
                return {"message": "Country not found", "status": "error"}

            if city_details and len(city_details) > 0:
                city = city_details[0]["name"]
            else:
                return {"message": "Country not found", "status": "error"}

            shipment = client.shipment.create(
                # carrier_accounts=["ca_c42e6d3b0c3c4964ae880ce2f0e62588"],
                # service="Express",
                to_address={
                    "name": userAddressDetails["full_name"],  # "Dr. Steve Brule",
                    "street1": userAddressDetails[
                        "roadName_area_colony"
                    ],  # "179 N Harbor Dr",
                    "city": city,  # "Redondo Beach",
                    "state": state,  # "CA",
                    "zip": userAddressDetails["pin_number"],  # "90277",
                    "country": country,  # "US",
                    "phone": userAddressDetails["phone_number"],  # "4153334444",
                    "email": data["email"],  # "dr_steve_brule@gmail.com",
                },
                # to_address={
                #     "name": "Dr. Steve Brule",
                #     "street1":"Bapuji Nagar Lane No 5 67",
                #     "city": "Bhubaneswar",
                #     "state": "OD",
                #     "zip": "751009",
                #     "country": "IN",
                #     "phone": userAddressDetails["phone_number"],  # "4153334444",
                #     "email": data["email"],  # "dr_steve_brule@gmail.com",
                # },
                from_address={
                    "name": "EasyPost",
                    "street1": "417 Montgomery Street",
                    "street2": "5th Floor",
                    "city": "San Francisco",
                    "state": "CA",
                    "zip": "94104",
                    "country": "US",
                    "phone": "4153334444",
                    "email": "support@easypost.com",
                },
                parcel={
                    "length": 20.2,
                    "width": 10.9,
                    "height": 5,
                    "weight": 65.9,
                },
            )
            return {
                "data": json.loads(json.dumps(shipment.to_dict())),
                "status": "success",
            }

        else:
            return {"message": "Please select address", "status": "error"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def buy_shipment_for_deliver(shp_id: str, rates_index: int):
    try:
        retrieved_shipment = client.shipment.retrieve(shp_id)
        print(retrieved_shipment)
        print(retrieved_shipment.lowest_rate())
        print(retrieved_shipment.rates[rates_index])

        shipment = client.shipment.buy(
            retrieved_shipment.id,
            rate=retrieved_shipment.rates[rates_index],
            # insurance=249.99,
        )

        return {"data": json.loads(json.dumps(shipment.to_dict())), "status": "success"}
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


def create_return_request(request, order_id):
    try:
        orderData = orderService.get_order_details_by_id(request, order_id)
        if orderData["status"] == "success" and len(orderData["data"]) > 0:
            shippingData = orderData["data"][0]["shipping_details"]
            if shippingData["status"] == "success" and len(shippingData["data"]) > 0:
                buyer_address = shippingData["data"]["buyer_address"]["id"]
                from_address = shippingData["data"]["from_address"]["id"]
                parcel_id = shippingData["data"]["parcel"]["id"]

                client = easypost.EasyPostClient("2TDp15wsUbcC95Z42Y4BrQ")

                shipment = client.shipment.create(
                    to_address={"id": buyer_address},
                    from_address={"id": from_address},
                    parcel={"id": parcel_id},
                    is_return=True,
                )

                db["order"].update_one(
                    {"_id": ObjectId(order_id)},
                    {
                        "$set": {
                            "status": 6,
                            "return_request_details": json.loads(
                                json.dumps(shipment.to_dict())
                            ),
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


def check_return_status(request, shipping_id):
    try:
        shipment = client.shipment.retrieve(shipping_id)
        return {
            "message": json.loads(json.dumps(shipment.to_dict())),
            "status": "success",
        }

    except Exception as e:
        return {"message": str(e), "status": "error"}
