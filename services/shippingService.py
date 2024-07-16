from fastapi.encoders import jsonable_encoder
import easypost
import json


api_key = "2TDp15wsUbcC95Z42Y4BrQ"
client = easypost.EasyPostClient(api_key)


def validate_address():
    try:
        address = client.address.create(
            verify_strict=True,
            street1="Bapuji Nagar Lane No 5 67",
            city="Bhubaneswar",
            state="OD",
            zip="751009",
            country="IN",
            email="test@example.com",
            phone="5555555555",
        )
        return {"data": json.loads(json.dumps(address.to_dict())), "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def create_shipment_and_get_rates():
    try:
        shipment = client.shipment.create(
            # carrier_accounts=["ca_c42e6d3b0c3c4964ae880ce2f0e62588"],
            # service="Express",
            to_address={
                "name": "Dr. Steve Brule",
                "street1": "179 N Harbor Dr",
                "city": "Redondo Beach",
                "state": "CA",
                "zip": "90277",
                "country": "US",
                "phone": "4153334444",
                "email": "dr_steve_brule@gmail.com",
            },
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

        return {"data": json.loads(json.dumps(shipment.to_dict())), "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def buy_shipment_for_deliver():
    try:
        retrieved_shipment = client.shipment.retrieve(
            "shp_62d9901cc785463bbb816bede9769f6b"
        )

        shipment = client.shipment.buy(
            retrieved_shipment.id,
            rate=retrieved_shipment.lowest_rate(),
            # insurance=249.99,
        )

        return {"data": json.loads(json.dumps(shipment.to_dict())), "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def track_order_by_id():
    try:
        tracker = client.tracker.retrieve("trk_d58e98dcfc96452083a496b4ba3b9fbe")
        return {"data": json.loads(json.dumps(tracker.to_dict())), "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}
