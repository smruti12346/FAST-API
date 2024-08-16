from fastapi import APIRouter, Request
import services.locationService as locationService

router = APIRouter()

@router.get("/get_all_country/", tags=['LOCATION MANAGEMENT'])
def get_all_country(request: Request):
    return locationService.get_all_country(request)


@router.get("/get_states_by_country/{country_code}", tags=['LOCATION MANAGEMENT'])
def get_states_by_country(country_code: str):
    return locationService.get_states_by_country(country_code)


@router.get("/get_city_by_country_and_state/{country_code}/{state_code}", tags=['LOCATION MANAGEMENT'])
def get_city_by_country_and_state(country_code: str, state_code: str):
    return locationService.get_city_by_country_and_state(country_code, state_code)