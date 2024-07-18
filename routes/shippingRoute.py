from fastapi import APIRouter, Depends
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
def track_order_by_id():
    return shippingService.track_order_by_id()