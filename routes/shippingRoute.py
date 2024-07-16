from fastapi import APIRouter
import services.shippingService as shippingService

router = APIRouter()

@router.post("/validate-address/")
def validate_address():
    return shippingService.validate_address()

@router.post("/create-shipment-and-get-rates/")
def create_shipment_and_get_rates():
    return shippingService.create_shipment_and_get_rates()

@router.post("/buy-shipment-for-deliver/")
def buy_shipment_for_deliver():
    return shippingService.buy_shipment_for_deliver()

@router.post("/track-order-by-id/")
def track_order_by_id():
    return shippingService.track_order_by_id()