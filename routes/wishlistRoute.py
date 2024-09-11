from fastapi import APIRouter, Depends, Request
import services.userService as userService
import services.wishlistService as wishlistService

router = APIRouter()


@router.post("/add-to-wishlist/{product_id}", tags=['WISHLIST MANAGEMENT'])
def create(product_id: str, token: str = Depends(userService.get_current_user)):
    if "_id" in token:
        return wishlistService.create(product_id, str(token["_id"]))
    else:
        return {"message": "Please Login First", "status": "error"}
    
@router.get("/view-all-wishlist/{page}", tags=['WISHLIST MANAGEMENT'])
def view(request: Request, page: int, show_page: int, token: str = Depends(userService.get_current_user)):
    if "_id" in token:
        return wishlistService.view(request, page, show_page, str(token["_id"]))
    else:
        return {"message": "Please Login First", "status": "error"}
    
@router.delete("/delete-wishlist/{wishlist_id}", tags=['WISHLIST MANAGEMENT'])
def delete(wishlist_id: str, token: str = Depends(userService.get_current_user)):
    if "_id" in token:
        return wishlistService.delete(wishlist_id)
    else:
        return {"message": "Please Login First", "status": "error"}