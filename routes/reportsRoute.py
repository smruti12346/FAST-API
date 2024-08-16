from fastapi import APIRouter, Request
import services.reportsService as reportsService

router = APIRouter()

@router.post("/user-pending-and-placed-order-return-request-count/", tags=['REPORTS'])
def user_pending_and_placed_order_return_request_count(start_date:str, end_date:str):
    return reportsService.user_pending_and_placed_order_return_request_count(start_date, end_date)

@router.post("/get-data-using-start-date-end-date/", tags=['REPORTS'])
def get_data_using_start_date_end_date(start_date:str, end_date:str):
    return reportsService.get_data_using_start_date_end_date(start_date, end_date)

@router.get("/top-selling-products/", tags=['REPORTS'])
def top_selling_products(request:Request, start_date:str, end_date:str):
    return reportsService.top_selling_products(request, start_date, end_date)
