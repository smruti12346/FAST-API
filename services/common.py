from math import ceil
from PIL import Image
import os

def paginate(collection, query, page=1, page_size=10):
    try:
        skip = (page - 1) * page_size
        pipeline = query + [{"$skip": skip}, {"$limit": page_size}]
        count_query = list(query)
        count_query.append({"$group": {"_id": None, "count": {"$sum": 1}}})
        count_result = list(collection.aggregate(count_query))
        total_count = count_result[0]["count"] if count_result else 0
        total_pages = ceil(total_count / page_size)
        page_data = list(collection.aggregate(pipeline))
        return {
            "data": page_data,
            "total": total_count,
            "page": page,
            "pages": total_pages,
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