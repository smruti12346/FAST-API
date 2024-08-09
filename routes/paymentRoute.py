from fastapi import APIRouter, Body, Request
import services.paymentService as paymentService
from Models.Payment import PaymentModel

router = APIRouter()


@router.post("/payment-details/")
def create(payment_details: PaymentModel = Body(...)):
    return paymentService.create(payment_details)


@router.get("/view-payment-details/{page}")
def view(request: Request, page: int, show_page: int):
    return paymentService.view(request, page, show_page)

@router.get("/view-payment-details-by-status/{status}")
def view_by_status(status: int):
    return paymentService.view_by_status(status)

@router.put("/payment-details/{payment_id}")
def update(payment_id: str, payment_details: PaymentModel = Body(...)):
    return paymentService.update(payment_id, payment_details)


@router.delete("/payment-details/{payment_id}")
def delete(payment_id: str):
    return paymentService.delete(payment_id)


@router.post("/change-payment-status/{payment_id}")
def change_status(payment_id: str):
    return paymentService.change_status(payment_id)


@router.post("/create-order/")
def create_paypal_order(total_amount: float, currency: str = "USD"):
    return paymentService.create_paypal_order(total_amount, currency)


@router.post("/capture-order/")
def capture_paypal_order(order_id: str):
    return paymentService.capture_paypal_order(order_id)


@router.get("/get-order-details/")
def get_paypal_order_details(order_id: str):
    return paymentService.get_paypal_order_details(order_id)


@router.post("/refund-payment/")
def refund_paypal_payment(order_id: str, reference_id: str):
    return paymentService.refund_paypal_payment(order_id, reference_id)