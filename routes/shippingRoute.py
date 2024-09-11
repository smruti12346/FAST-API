from fastapi import APIRouter, Depends, Request, Body
import services.shippingService as shippingService
import services.userService as userService
from Models.Shipping import ShippingModel, ShippingUpdateModel
from typing import Optional

router = APIRouter()


@router.post("/shipping-details/", tags=["SHIPPING CREDENTIAL DETAILS MANAGEMENT"])
def create(
    shipping_details: ShippingModel = Body(...),
    token: str = Depends(userService.get_current_user),
):
    if "_id" in token:
        return shippingService.create(shipping_details, str(token["_id"]))
    else:
        return {"message": "Please Login First", "status": "error"}


@router.get(
    "/view-shipping-details/{page}", tags=["SHIPPING CREDENTIAL DETAILS MANAGEMENT"]
)
def view(request: Request, page: int, show_page: int):
    return shippingService.view(request, page, show_page)


@router.get(
    "/view-shipping-details-by-status/{status}",
    tags=["SHIPPING CREDENTIAL DETAILS MANAGEMENT"],
)
def view_by_status(status: int):
    return shippingService.view_by_status(status)


@router.put(
    "/shipping-details/{shipping_id}", tags=["SHIPPING CREDENTIAL DETAILS MANAGEMENT"]
)
def update(
    shipping_id: str,
    shipping_details: ShippingUpdateModel = Body(...),
    token: str = Depends(userService.get_current_user),
):
    if "_id" in token:
        return shippingService.update(shipping_id, shipping_details)
    else:
        return {"message": "Please Login First", "status": "error"}


@router.delete(
    "/shipping-details/{shipping_id}", tags=["SHIPPING CREDENTIAL DETAILS MANAGEMENT"]
)
def delete(shipping_id: str, token: str = Depends(userService.get_current_user)):
    if "_id" in token:
        return shippingService.delete(shipping_id)
    else:
        return {"message": "Please Login First", "status": "error"}


@router.post(
    "/change-shipping-status/{shipping_id}",
    tags=["SHIPPING CREDENTIAL DETAILS MANAGEMENT"],
)
def change_status(shipping_id: str, token: str = Depends(userService.get_current_user)):
    if "_id" in token:
        return shippingService.change_status(shipping_id)
    else:
        return {"message": "Please Login First", "status": "error"}


# ======================================================================================================
# ======================================================================================================
# ======================================================================================================


@router.post("/validate-address/", tags=["SHIPPING MANAGEMENT"])
def validate_address(
    street1: Optional[str] = None,
    city: Optional[str] = None,
    state: Optional[str] = None,
    zip: Optional[str] = None,
    country: Optional[str] = None,
    email: Optional[str] = None,
    phone: Optional[str] = None,
):
    return shippingService.validate_address(
        street1, city, state, zip, country, email, phone
    )


@router.post("/create-shipment-and-get-rates/", tags=["SHIPPING MANAGEMENT"])
def create_shipment_and_get_rates(token: str = Depends(userService.get_current_user)):
    if "_id" in token:
        return shippingService.create_shipment_and_get_rates(token)
    else:
        return {"message": "Please Login First", "status": "error"}


@router.post("/buy-shipment-for-deliver/", tags=["SHIPPING MANAGEMENT"])
def buy_shipment_for_deliver():
    return shippingService.buy_shipment_for_deliver()


@router.post("/track-order-by-id/", tags=["SHIPPING MANAGEMENT"])
def track_order_by_id(trk_id: str):
    return shippingService.track_order_by_id(trk_id)


# @router.post("/create-return-request/", tags=["SHIPPING MANAGEMENT"])
# def create_return_request(request: Request, order_id: str):
#     return shippingService.create_return_request(request, order_id)


@router.post("/check-return-status/", tags=["SHIPPING MANAGEMENT"])
def check_return_status(request: Request, shipping_id: str):
    return shippingService.check_return_status(request, shipping_id)


@router.get("/create-shipping-label/", tags=["SHIPPING MANAGEMENT"])
def create_shipping_label():
    return shippingService.create_shipping_label()


@router.get("/get-address-using-zip-code/{zip_code}", tags=["SHIPPING MANAGEMENT"])
def get_address_using_zip_code(zip_code: int):
    return shippingService.get_address_using_zip_code(zip_code)
