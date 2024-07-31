from fastapi import APIRouter, Body, Request, Depends, BackgroundTasks
from Models.Order import OrderModel, InvoiceModel
import services.cartService as cartService
import services.userService as userService
import services.orderService as orderService

from typing import List

router = APIRouter()


@router.post("/add_to_cart/")
def add_to_cart(product_id: str, token: str = Depends(userService.get_current_user)):
    if "_id" in token:
        return cartService.add_to_cart(str(token["_id"]), product_id)
    else:
        return {"data": "Not authenticated", "status": "error"}


@router.post("/cart/")
def add_to_cart(request: Request, items: List[str] = Body(...)):
    return cartService.get_cart_details_by_product_arr(request, items)


@router.post("/get_all_cart_details_by_user_id/")
def get_all_cart_details_by_user_id(
    request: Request, token: str = Depends(userService.get_current_user)
):
    if "_id" in token:
        return cartService.get_all_cart_details_by_user_id(request, str(token["_id"]))
    else:
        return {"data": "Not authenticated", "status": "error"}


# @router.post("/get_all_cart_details_by_user_id/")
# def get_all_cart_details_by_user_id(request: Request, user_id: str):
#     return cartService.get_all_cart_details_by_user_id(request, user_id)


@router.post("/check_order_quantity/")
def check_order_quantity(product_id: str, varientArr: List[int]):
    return orderService.check_order_quantity(product_id, varientArr)


@router.post("/check_order_quantity_by_order/")
def check_order_quantity_by_order(product_details: List[OrderModel] = Body(...)):
    return orderService.check_order_quantity_by_order(product_details)


@router.post("/order_placed/")
def order_placed(
    product_details: List[OrderModel] = Body(...),
    token: str = Depends(userService.get_current_user),
):
    if "_id" in token:
        return orderService.order_placed(str(token["_id"]), product_details)
    else:
        return {"data": "Not authenticated", "status": "error"}


@router.get("/orders/")
def get_orders(request: Request):
    return orderService.get_orders(request)


@router.get("/get-all-orders/{page}")
def get_all_orders(request: Request, page: int, show_page: int):
    return orderService.get_all_orders(request, page, show_page)


@router.get("/get-orders-by-counts/{page}")
def get_orders_by_counts(
    request: Request,
    page: int,
    show_page: int,
):
    return orderService.get_orders_by_counts(request, page, show_page)


@router.get("/orders_by_user/{page}")
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
        return {"data": "Not authenticated", "status": "error"}


@router.put("/update-order-status/{order_id}")
def update_order_status(order_id: str, status: int, token: str = Depends(userService.get_current_user)):
    if "_id" in token:
        return orderService.update_order_status(order_id, status, str(token['_id']), token['user_type'])
    else:
        return {"data": "Not authenticated", "status": "error"}


# @router.post("/get-all-orders-status-wise/")
# def get_all_orders_status_wise(request:Request, status: List[int]):
#     return orderService.get_all_orders_status_wise(request, status)


@router.post("/get-all-orders-status-wise/{page}")
def get_all_orders_status_wise(
    request: Request, status: List[int], page: int, show_page: int
):
    return orderService.get_all_orders_status_wise(request, status, page, show_page)


@router.post("/get-all-orders-count-status-wise/")
def get_all_orders_count_status_wise():
    return orderService.get_all_orders_count_status_wise()


@router.post("/get-order-invoice/")
def get_order_invoice(data: InvoiceModel, background_tasks: BackgroundTasks):
    return orderService.get_order_invoice(data, background_tasks)


@router.post("/check-order-tracking-status-and-update-deliver-or-not/")
def check_order_tracking_status_and_update_deliver_or_not(request: Request):
    return orderService.check_order_tracking_status_and_update_deliver_or_not(request)


@router.post("/check-order-tracking-status-and-update-user-wise-deliver-or-not/")
def check_order_tracking_status_and_update_user_wise_deliver_or_not(
    request: Request, token: str = Depends(userService.get_current_user)
):
    if "_id" in token:
        return orderService.check_order_tracking_status_and_update_user_wise_deliver_or_not(
            request, str(token["_id"])
        )
    else:
        return {"data": "Not authenticated", "status": "error"}


