from math import ceil


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
