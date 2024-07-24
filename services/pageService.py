from db import db
from services.common import paginate
import re

collection = db["pages"]


def create_pages(data):
    try:
        data = data.dict()
        if collection.count_documents({"slug": data["slug"], "deleted_at": None}) != 0:
            return {"message": "slug already exist", "status": "error"}

        result = collection.insert_one(data)
        return {
            "message": "data inserted successfully",
            "_id": str(result.inserted_id),
            "status": "success",
        }
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_pages(request, page, show_page):
    try:
        pipeline = [
            {"$match": {"deleted_at": None}},
            {"$sort": {"created_at": 1}},
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "name": 1,
                    "slug": 1,
                    "components": 1,
                    "seo": 1,
                    "status": 1,
                    "deleted_at": 1,
                    "created_at": 1,
                    "created_by": 1,
                    "updated_at": 1,
                    "updated_by": 1,
                }
            },
        ]
        result = paginate(collection, pipeline, page, show_page)
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_all_pages(request):
    try:
        pipeline = [
            {"$match": {}},
            {
                "$addFields": {
                    "components_object_ids": {
                        "$map": {
                            "input": "$components",
                            "as": "component_id",
                            "in": {"$toObjectId": "$$component_id"},
                        }
                    }
                }
            },
            {
                "$lookup": {
                    "from": "component",
                    "localField": "components_object_ids",
                    "foreignField": "_id",
                    "as": "component_details",
                }
            },
            {
                "$project": {
                    "_id": {"$toString": "$_id"},
                    "name": 1,
                    "slug": 1,
                    "components": 1,
                    "seo": 1,
                    "status": 1,
                    "deleted_at": 1,
                    "created_at": 1,
                    "created_by": 1,
                    "updated_at": 1,
                    "updated_by": 1,
                    "component_details": {
                        "$map": {
                            "input": "$component_details",
                            "as": "component",
                            "in": {
                                "_id": {"$toString": "$$component._id"},
                                "name": "$$component.name",
                                "slug": "$$component.slug",
                                "fields": "$$component.fields",
                                "field_values": "$$component.field_values",
                                "description": "$$component.description",
                                "seo": "$$component.seo",
                                "status": "$$component.status",
                                "deleted_at": "$$component.deleted_at",
                                "created_at": "$$component.created_at",
                                "created_by": "$$component.created_by",
                                "updated_at": "$$component.updated_at",
                                "updated_by": "$$component.updated_by"
                            }
                        }
                    }
                }
            }
        ]

        result = list(collection.aggregate(pipeline))
        process_component_detail = process_component_details(result, request)

        # print(result)
        return {"data": process_component_detail, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def convert_to_underscore(input_string):
    return re.sub(r'\s+', '_', input_string)




def process_component_details(data, request):
    for item in data:
        for component in item.get('component_details', []):
            # Iterate through fields
            for field in component.get('fields', []):
                if field.get('field_type') == 'file':
                    field_name = field.get('field_name')
                    # Iterate through field_values
                    for field_value in component.get('field_values', []):
                        if field_name in field_value:
                            # Construct the new key for the image path
                            image_path_imageUrl_key = f"{convert_to_underscore(field_name)}_imageUrl_path"
                            image_path_imageUrl100_key = f"{convert_to_underscore(field_name)}_imageUrl100_path"
                            image_path_imageUrl300_key = f"{convert_to_underscore(field_name)}_imageUrl300_path"
                            field_value[image_path_imageUrl_key] = str(request.base_url)[:-1] + "/uploads/component/" + field_value[field_name]
                            field_value[image_path_imageUrl100_key] = str(request.base_url)[:-1] + "/uploads/component/100/" + field_value[field_name]
                            field_value[image_path_imageUrl300_key] = str(request.base_url)[:-1] + "/uploads/component/300/" + field_value[field_name]
    return data