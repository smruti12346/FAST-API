from fastapi import APIRouter, Depends, Body, Request

import services.pageService as pageService

from Models.Pages import CreatePagesRequest

router = APIRouter()

@router.post("/create_pages/")
def create_pages(CreatePagesRequest: CreatePagesRequest = Body(...)):
    return pageService.create_pages(CreatePagesRequest)


@router.get("/pages/{page}")
def get_pages(request: Request, page: int, show_page: int):
    return pageService.get_pages(request, page, show_page)

@router.get("/get-all-pages")
def get_all_pages(request: Request):
    return pageService.get_all_pages(request)
