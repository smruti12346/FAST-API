from fastapi import APIRouter
import services.reportsService as reportsService

router = APIRouter()

@router.post("/user-pending-and-placed-order-return-request-count/")
def user_pending_and_placed_order_return_request_count():
    return reportsService.user_pending_and_placed_order_return_request_count()

