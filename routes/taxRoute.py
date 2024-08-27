from fastapi import APIRouter, Depends, Request, Body
import services.taxService as taxService
import services.userService as userService
from Models.Tax import TaxModel

router = APIRouter()


@router.post("/tax-details/", tags=["TAX DETAILS MANAGEMENT"])
def create(
    tax_details: TaxModel = Body(...),
    token: str = Depends(userService.get_current_user),
):
    if "_id" in token:
        return taxService.create(tax_details, str(token["_id"]))
    else:
        return {"message": "Not authenticated", "status": "error"}


@router.get("/view-tax-details/{page}", tags=["TAX DETAILS MANAGEMENT"])
def view(page: int, show_page: int):
    return taxService.view(page, show_page)


@router.put("/tax-details/{tax_id}", tags=["TAX DETAILS MANAGEMENT"])
def update(
    tax_id: str,
    tax_details: TaxModel = Body(...),
    token: str = Depends(userService.get_current_user),
):
    if "_id" in token:
        return taxService.update(tax_id, tax_details)
    else:
        return {"message": "Not authenticated", "status": "error"}


@router.delete("/tax-details/{tax_id}", tags=["TAX DETAILS MANAGEMENT"])
def delete(tax_id: str, token: str = Depends(userService.get_current_user)):
    if "_id" in token:
        return taxService.delete(tax_id)
    else:
        return {"message": "Not authenticated", "status": "error"}
