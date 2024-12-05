from fastapi import APIRouter, Depends, Request, Body
import services.warentyService as warentyService
import services.userService as userService
from Models.warenty import WarentyModel, WarentyUpdateModel

router = APIRouter()


@router.post("/warenty-details/", tags=["WARENTY DETAILS MANAGEMENT"])
def create(
    warenty_details: WarentyModel = Body(...),
    token: str = Depends(userService.get_current_user),
):
    if "_id" in token:
        return warentyService.create(warenty_details, str(token["_id"]))
    else:
        return {"message": "Please Login First", "status": "error"}


@router.get("/view-warenty-details/{page}", tags=["WARENTY DETAILS MANAGEMENT"])
def view(page: int, show_page: int, request: Request,):
    return warentyService.view(request, page, show_page)


@router.put("/warenty-details/{warenty_id}", tags=["WARENTY DETAILS MANAGEMENT"])
def update(
    warenty_id: str,
    warenty_details: WarentyUpdateModel = Body(...),
    token: str = Depends(userService.get_current_user),
):
    if "_id" in token:
        return warentyService.update(warenty_id, warenty_details, str(token["_id"]))
    else:
        return {"message": "Please Login First", "status": "error"}


# @router.delete("/warenty-details/{warenty_id}", tags=["WARENTY DETAILS MANAGEMENT"])
# def delete(warenty_id: str, token: str = Depends(userService.get_current_user)):
#     if "_id" in token:
#         return warentyService.delete(warenty_id)
#     else:
#         return {"message": "Please Login First", "status": "error"}
