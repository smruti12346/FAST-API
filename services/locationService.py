from db import db

collection = db["location"]


def get_all_country(request):
    try:
        result = collection.find({"deleted_at": None}, {"name": 1, "id": 1, "_id": 1})
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_states_by_country(country_id):
    try:
        pipeline = [
            {"$match": {"id": country_id}},
            {"$unwind": "$states"},
            {"$project": {"_id": 0, "id": "$states.id", "name": "$states.name"}},
        ]
        result = list(db.location.aggregate(pipeline))
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_city_by_country_and_state(country_id, state_id):
    try:
        pipeline = [
            {"$match": {"id": country_id}},
            {"$unwind": "$states"},
            {"$match": {"states.id": state_id}},
            {"$unwind": "$states.cities"},
            {
                "$project": {
                    "_id": 0,
                    "id": "$states.cities.id",
                    "name": "$states.cities.name",
                }
            },
        ]
        result = list(db.location.aggregate(pipeline))
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}
