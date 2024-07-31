from fastapi import APIRouter, Depends, Request
import services.shippingService as shippingService
import services.userService as userService

router = APIRouter()


@router.post("/validate-address/")
def validate_address():
    return shippingService.validate_address()


@router.post("/create-shipment-and-get-rates/")
def create_shipment_and_get_rates(token: str = Depends(userService.get_current_user)):
    if "_id" in token:
        return shippingService.create_shipment_and_get_rates(token)
    else:
        return {"data": "Not authenticated", "status": "error"}


@router.post("/buy-shipment-for-deliver/")
def buy_shipment_for_deliver():
    return shippingService.buy_shipment_for_deliver()


@router.post("/track-order-by-id/")
def track_order_by_id(trk_id: str):
    return shippingService.track_order_by_id(trk_id)


@router.post("/create-return-request/")
def create_return_request(request: Request, order_id: str):
    return shippingService.create_return_request(request, order_id)

@router.post("/check-return-status/")
def check_return_status(request: Request, shipping_id: str):
    return shippingService.check_return_status(request, shipping_id)
