from fastapi import APIRouter, Depends, Body, Request

import services.componentService as componentService

from Models.Component import ComponentData

router = APIRouter()


@router.post("/create_component/", tags=["DYNAMIC PAGE'S COMPONENT MANAGEMENT"])
def create_component(componentData: ComponentData = Body(...)):
    return componentService.create_component(componentData)


@router.get("/component/{page}", tags=["DYNAMIC PAGE'S COMPONENT MANAGEMENT"])
def get_component(request: Request, page: int, show_page: int):
    return componentService.get_component(request, page, show_page)


@router.get("/get-all-component", tags=["DYNAMIC PAGE'S COMPONENT MANAGEMENT"])
def get_all_component(request: Request):
    return componentService.get_all_component(request)


@router.post("/add-component-details/{id}", tags=["DYNAMIC PAGE'S COMPONENT MANAGEMENT"])
async def add_component_details(request: Request, id: str):
    form_data = await request.form()
    return await componentService.add_component_details(form_data, id)


@router.delete("/delete-component-details/{_id}/{id}", tags=["DYNAMIC PAGE'S COMPONENT MANAGEMENT"])
def delete_component_details(request: Request, _id: str, id: str):
    return componentService.delete_component_details(request, _id, id)
