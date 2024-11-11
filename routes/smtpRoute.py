from fastapi import APIRouter, Depends, Body
import services.smtpService as smtpService
import services.userService as userService
from Models.smtp import SmtpModel

router = APIRouter()


@router.post("/smtp-details/", tags=["SMTP DETAILS MANAGEMENT"])
def create(
    smtp_details: SmtpModel = Body(...),
    token: str = Depends(userService.get_current_user),
):
    if "_id" in token:
        return smtpService.create(smtp_details, str(token["_id"]))
    else:
        return {"message": "Please Login First", "status": "error"}


@router.get("/view-smtp-details/{page}", tags=["SMTP DETAILS MANAGEMENT"])
def view(page: int, show_page: int):
    return smtpService.view(page, show_page)


@router.put("/smtp-details/{smtp_id}", tags=["SMTP DETAILS MANAGEMENT"])
def update(
    smtp_id: str,
    smtp_details: SmtpModel = Body(...),
    token: str = Depends(userService.get_current_user),
):
    if "_id" in token:
        return smtpService.update(smtp_id, smtp_details)
    else:
        return {"message": "Please Login First", "status": "error"}
    
@router.post(
    "/change-smtp-status/{smtp_id}",
    tags=["SMTP CREDENTIAL DETAILS MANAGEMENT"],
)
def change_status(smtp_id: str, token: str = Depends(userService.get_current_user)):
    if "_id" in token:
        return smtpService.change_status(smtp_id)
    else:
        return {"message": "Please Login First", "status": "error"}


@router.delete("/smtp-details/{smtp_id}", tags=["SMTP DETAILS MANAGEMENT"])
def delete(smtp_id: str, token: str = Depends(userService.get_current_user)):
    if "_id" in token:
        return smtpService.delete(smtp_id)
    else:
        return {"message": "Please Login First", "status": "error"}