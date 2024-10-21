from fastapi import APIRouter
import services.scripts as scripts

router = APIRouter()

@router.post("/generate-dummy-products/")
def generate_dummy_product():
    return scripts.generate_dummy_product()

@router.post("/generate-dummy-orders/")
def generate_dummy_order_route_handle():
    return scripts.generate_dummy_order_route_handle()

@router.post("/update-catgory-arr/{parent_id}")
def update_category_arr(parent_id:int):
    return scripts.update_category_arr(parent_id, None)

@router.post("/get-all-category-arr-hirarchy/")
def get_all_category_arr_hirarchy():
    return scripts.get_all_category_arr_hirarchy()

@router.post("/convert-to-valid-slug/")
def convert_to_valid_slug():
    return scripts.convert_to_valid_slug()

@router.post("/fix-duplicate-slugs/")
def fix_duplicate_slugs():
    return scripts.fix_duplicate_slugs()