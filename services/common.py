from math import ceil
import math
from PIL import Image
import os

def replace_nan_with_default(data, default_value=0):
    if isinstance(data, list):
        return [replace_nan_with_default(item, default_value) for item in data]
    elif isinstance(data, dict):
        return {key: replace_nan_with_default(value, default_value) for key, value in data.items()}
    elif isinstance(data, float) and (math.isnan(data) or math.isinf(data)):
        return default_value
    return data

def paginate(collection, query, page=1, page_size=10):
    try:
        skip = (page - 1) * page_size
        # Check if the query contains a $match stage
        match_stage = next((stage for stage in query if "$match" in stage), None)
        # Create the total pipeline with conditional match stage
        total_pipeline = [match_stage] if match_stage else []
        total_pipeline.append({"$group": {"_id": None, "count": {"$sum": 1}}})
        # Create the data pipeline
        data_pipeline = query + [
            {"$skip": skip},
            {"$limit": page_size}
        ]
        # Execute the pipelines using $facet
        pipeline = [
            {"$facet": {
                "data": data_pipeline,
                "total": total_pipeline
            }}
        ]
        result = list(collection.aggregate(pipeline))[0]
        page_data = replace_nan_with_default(result["data"]) 
        total_count = result["total"][0]["count"] if result["total"] else 0
        total_pages = ceil(total_count / page_size)

        return {
            "data": page_data,
            "total": total_count,
            "page": page,
            "pages": total_pages,
            "start_count": skip,
            "end_count": min(skip + page_size, total_count)
        }

    except Exception as e:
        return {"message": str(e), "status": "error"}


def convert_oid_to_str(maindata):
    data = []
    for doc in maindata:
        doc["_id"] = str(doc["_id"])
        data.append(doc)
    return data


def resize_image(filename, mainFileName, PATH_FILES):

    sizes = [
        {"width": 100, "height": 100, "path": "100/"},
        {"width": 300, "height": 300, "path": "300/"},
    ]

    for size in sizes:
        os.makedirs(PATH_FILES + size["path"], exist_ok=True)
        size_defined = size["width"], size["height"]
        image = Image.open(PATH_FILES + mainFileName, mode="r")
        image.thumbnail(size_defined)
        image.save(
            PATH_FILES + size["path"] + filename + ".webp",
            "webp",
            optimize=True,
            quality=10,
        )
    image = Image.open(PATH_FILES + mainFileName, mode="r")
    image.save(PATH_FILES + filename + ".webp", "webp", optimize=True, quality=10)
    # os.remove(PATH_FILES + mainFileName)