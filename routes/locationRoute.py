from fastapi import APIRouter, Request
import services.locationService as locationService

router = APIRouter()

@router.get("/get_all_country/")
def get_all_country(request: Request):
    return locationService.get_all_country(request)


@router.get("/get_states_by_country/{country_id}")
def get_states_by_country(country_id: int):
    return locationService.get_states_by_country(country_id)


@router.get("/get_city_by_country_and_state/{country_id}/{state_id}")
def get_city_by_country_and_state(country_id: int, state_id: int):
    return locationService.get_city_by_country_and_state(country_id, state_id)