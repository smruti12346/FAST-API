from fastapi import APIRouter
import services.scripts as scripts

router = APIRouter()

@router.post("/generate-dummy-products/")
def generate_dummy_product():
    return scripts.generate_dummy_product()

@router.post("/generate-dummy-orders/")
def generate_dummy_order_route_handle():
    return scripts.generate_dummy_order_route_handle()