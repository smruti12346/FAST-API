from fastapi import APIRouter, Depends, Request, Body
import services.discountCouponService as discountCouponService
import services.userService as userService
from Models.discountCoupon import DiscountCouponModel, DiscountCouponUpdateModel

router = APIRouter()


@router.post("/discount-coupon-details/", tags=["DISCOUNT COUPON DETAILS MANAGEMENT"])
def create(
    discount_details: DiscountCouponModel = Body(...),
    token: str = Depends(userService.get_current_user),
):
    if "_id" in token:
        return discountCouponService.create(discount_details)
    else:
        return {"message": "Not authenticated", "status": "error"}


@router.get(
    "/view-discount-coupon-details/{page}", tags=["DISCOUNT COUPON DETAILS MANAGEMENT"]
)
def view(request: Request, page: int, show_page: int):
    return discountCouponService.view(request, page, show_page)


@router.get(
    "/view-discount-coupon-details-by-status/{status}",
    tags=["DISCOUNT COUPON DETAILS MANAGEMENT"],
)
def view_by_status(status: int):
    return discountCouponService.view_by_status(status)

@router.get(
    "/view-discount-coupon-details-by-coupon-code/{coupon_code}",
    tags=["DISCOUNT COUPON DETAILS MANAGEMENT"],
)
def view_by_coupon_code(coupon_code: str):
    return discountCouponService.view_by_coupon_code(coupon_code)


@router.get(
    "/view-discount-coupon-details-by-coupon-code-and-customer-id/{coupon_code}",
    tags=["DISCOUNT COUPON DETAILS MANAGEMENT"],
)
def view_by_coupon_code_with_customer_id(coupon_code: str, token: str = Depends(userService.get_current_user)):
    if "_id" in token:
        return discountCouponService.view_by_coupon_code_with_customer_id(coupon_code,  str(token["_id"]))
    else:
        return {"message": "Not authenticated", "status": "error"}


@router.put(
    "/discount-coupon-details/{discount_id}", tags=["DISCOUNT COUPON DETAILS MANAGEMENT"]
)
def update(
    discount_id: str,
    discount_details: DiscountCouponUpdateModel = Body(...),
    token: str = Depends(userService.get_current_user),
):
    if "_id" in token:
        return discountCouponService.update(discount_id, discount_details)
    else:
        return {"message": "Not authenticated", "status": "error"}


@router.delete(
    "/discount-coupon-details/{discount_id}", tags=["DISCOUNT COUPON DETAILS MANAGEMENT"]
)
def delete(discount_id: str, token: str = Depends(userService.get_current_user)):
    if "_id" in token:
        return discountCouponService.delete(discount_id)
    else:
        return {"message": "Not authenticated", "status": "error"}


@router.post(
    "/change-discount-coupon-status/{discount_id}",
    tags=["DISCOUNT COUPON DETAILS MANAGEMENT"],
)
def change_status(discount_id: str, token: str = Depends(userService.get_current_user)):
    if "_id" in token:
        return discountCouponService.change_status(discount_id)
    else:
        return {"message": "Not authenticated", "status": "error"}
