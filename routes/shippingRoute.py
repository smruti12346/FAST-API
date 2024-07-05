from fastapi import APIRouter
import services.shippingService as shippingService

router = APIRouter()

json_request = {
    "AddressValidateRequest": {
        "@USERID": "963ZVUIM7386",
        "Revision": "1",
        "Address": {
            "Address1": "Suite 6100",
            "Address2": "185 Berry St",
            "City": "San Francisco",
            "State": "CA",
            "Zip5": "94556",
            "Zip4": "",
        },
    }
}

@router.post("/get-usps-shipping-rate/")
def get_usps_shipping_rate():
    return shippingService.get_usps_shipping_rate(json_request)