from fastapi import APIRouter, Depends, Body
import services.newsLetterService as newsLetterService
import services.userService as userService
from Models.newsLetter import NewsLetterModel

router = APIRouter()


@router.post("/news-letter-details/", tags=["NEWSLETTER DETAILS MANAGEMENT"])
def create(newsletter_details: NewsLetterModel = Body(...)):
    return newsLetterService.create(newsletter_details)


@router.get("/view-news-letter-details/{page}", tags=["NEWSLETTER DETAILS MANAGEMENT"])
def view(page: int, show_page: int):
    return newsLetterService.view(page, show_page)


@router.put("/news-letter-details/{newsletter_id}", tags=["NEWSLETTER DETAILS MANAGEMENT"])
def update(
    newsletter_id: str,
    newsletter_details: NewsLetterModel = Body(...),
    token: str = Depends(userService.get_current_user),
):
    if "_id" in token:
        return newsLetterService.update(newsletter_id, newsletter_details)
    else:
        return {"message": "Please Login First", "status": "error"}


@router.post(
    "/change-news-letter-status/{newsletter_id}",
    tags=["NEWSLETTER DETAILS MANAGEMENT"],
)
def change_status(newsletter_id: str, token: str = Depends(userService.get_current_user)):
    if "_id" in token:
        return newsLetterService.change_status(newsletter_id)
    else:
        return {"message": "Please Login First", "status": "error"}


@router.delete("/news-letter-details/{newsletter_id}", tags=["NEWSLETTER DETAILS MANAGEMENT"])
def delete(newsletter_id: str, token: str = Depends(userService.get_current_user)):
    if "_id" in token:
        return newsLetterService.delete(newsletter_id)
    else:
        return {"message": "Please Login First", "status": "error"}
