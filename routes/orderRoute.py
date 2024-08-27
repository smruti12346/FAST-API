from fastapi import APIRouter, Body, Request, Depends, BackgroundTasks
from Models.Order import OrderModel, InvoiceModel
import services.cartService as cartService
import services.userService as userService
import services.orderService as orderService

from typing import List

router = APIRouter()

# ======================================================================================================
# ======================================================================================================
# ======================================================================================================
# @router.post("/add_to_cart/")
# def add_to_cart(product_id: str, token: str = Depends(userService.get_current_user)):
#     if "_id" in token:
#         return cartService.add_to_cart(str(token["_id"]), product_id)
#     else:
#         return {"message": "Not authenticated", "status": "error"}


# ======================================================================================================
# ======================================================================================================
# ======================================================================================================
@router.post("/cart/", tags=["CART MANAGEMENT"])
def add_to_cart(request: Request, items: List[str] = Body(...)):
    return cartService.get_cart_details_by_product_arr(request, items)


@router.post("/get_all_cart_details_by_user_id/", tags=["CART MANAGEMENT"])
def get_all_cart_details_by_user_id(
    request: Request, token: str = Depends(userService.get_current_user)
):
    if "_id" in token:
        return cartService.get_all_cart_details_by_user_id(request, str(token["_id"]))
    else:
        return {"message": "Not authenticated", "status": "error"}


@router.post("/check_order_quantity/", tags=["CART MANAGEMENT"])
def check_order_quantity(product_id: str, varientArr: List[int]):
    return orderService.check_order_quantity(product_id, varientArr)


@router.post("/check_order_quantity_by_order/", tags=["CART MANAGEMENT"])
def check_order_quantity_by_order(product_details: List[OrderModel] = Body(...)):
    return orderService.check_order_quantity_by_order(product_details)


# ======================================================================================================
# ======================================================================================================
# ======================================================================================================
@router.post("/order_create/", tags=["ORDER MANAGEMENT"])
def order_create(
    product_details: List[OrderModel] = Body(...),
    token: str = Depends(userService.get_current_user),
):
    if "_id" in token:
        primary_address = [entry for entry in token['address'] if entry['primary_status'] == 1]
        country_code = primary_address[0]['country_code']
        return orderService.order_create(str(token["_id"]), country_code, product_details)
    else:
        return {"message": "Not authenticated", "status": "error"}


@router.post("/capture-created-order/", tags=["ORDER MANAGEMENT"])
def capture_created_order(payment_id: str):
    return orderService.capture_created_order("hi", payment_id)


# def capture_created_order(
#     payment_id: str, token: str = Depends(userService.get_current_user)
# ):
#     if "_id" in token:
#         return orderService.capture_created_order(str(token["_id"]), payment_id)
#     else:
#         return {"message": "Not authenticated", "status": "error"}


@router.get("/orders_by_user/{page}", tags=["ORDER MANAGEMENT"])
def get_all_orders_by_user(
    request: Request,
    page: int,
    show_page: int,
    token: str = Depends(userService.get_current_user),
):
    if "_id" in token:
        return orderService.get_all_orders_by_user(
            request, str(token["_id"]), page, show_page
        )
    else:
        return {"message": "Not authenticated", "status": "error"}


@router.put("/update-order-status/{order_id}", tags=["ORDER MANAGEMENT"])
def update_order_status(
    order_id: str, status: int, token: str = Depends(userService.get_current_user)
):
    if "_id" in token:
        return orderService.update_order_status(
            order_id, status, str(token["_id"]), token["user_type"]
        )
    else:
        return {"message": "Not authenticated", "status": "error"}


@router.post(
    "/check-order-tracking-status-and-update-deliver-or-not/", tags=["ORDER MANAGEMENT"]
)
def check_order_tracking_status_and_update_deliver_or_not(request: Request):
    return orderService.check_order_tracking_status_and_update_deliver_or_not(request)


@router.post(
    "/check-order-tracking-status-and-update-user-wise-deliver-or-not/",
    tags=["ORDER MANAGEMENT"],
)
def check_order_tracking_status_and_update_user_wise_deliver_or_not(
    request: Request, token: str = Depends(userService.get_current_user)
):
    if "_id" in token:
        return orderService.check_order_tracking_status_and_update_user_wise_deliver_or_not(
            request, str(token["_id"])
        )
    else:
        return {"message": "Not authenticated", "status": "error"}


@router.post("/create-order-return-request/", tags=["SHIPPING MANAGEMENT"])
def create_order_return_request(
    request: Request, order_id: str, token: str = Depends(userService.get_current_user)
):
    if "_id" in token:
        return orderService.create_order_return_request(request, order_id)
    else:
        return {"message": "Not authenticated", "status": "error"}


# ======================================================================================================
# ======================================================================================================
# ======================================================================================================
@router.get("/orders/", tags=["ORDER REPORTS"])
def get_orders(request: Request):
    return orderService.get_orders(request)


@router.get("/get-all-orders/{page}", tags=["ORDER REPORTS"])
def get_all_orders(request: Request, page: int, show_page: int):
    return orderService.get_all_orders(request, page, show_page)


@router.get("/get-orders-by-counts/{page}", tags=["ORDER REPORTS"])
def get_orders_by_counts(
    request: Request,
    page: int,
    show_page: int,
):
    return orderService.get_orders_by_counts(request, page, show_page)


@router.post("/get-all-orders-status-wise/{page}", tags=["ORDER REPORTS"])
def get_all_orders_status_wise(
    request: Request, status: List[int], page: int, show_page: int
):
    return orderService.get_all_orders_status_wise(request, status, page, show_page)


@router.post("/get-all-orders-count-status-wise/", tags=["ORDER REPORTS"])
def get_all_orders_count_status_wise():
    return orderService.get_all_orders_count_status_wise()


@router.post("/get-order-invoice/", tags=["ORDER REPORTS"])
def get_order_invoice(data: InvoiceModel, background_tasks: BackgroundTasks):
    return orderService.get_order_invoice(data, background_tasks)
