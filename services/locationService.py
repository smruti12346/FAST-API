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

def get_country_by_id(country_id: int):
    try:
        result = collection.find({"deleted_at": None, "id": country_id}, {"name": 1, "id": 1, "_id": 1, "iso2": 1})
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_states_by_state_id_and_country_id(country_id : int, state_id : int):
    try:
        pipeline = [
            {"$match": {"id": country_id}},
            {"$unwind": "$states"},
            {"$match": {"states.id": state_id}},
            {"$project": {"_id": 0, "id": "$states.id", "name": "$states.name", "state_code": "$states.state_code"}},
        ]
        result = list(db.location.aggregate(pipeline))
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_city_by_city_id_country_id_and_state_id(country_id, state_id, city_id):
    try:
        pipeline = [
            {"$match": {"id": country_id}},
            {"$unwind": "$states"},
            {"$match": {"states.id": state_id}},
            {"$unwind": "$states.cities"},
            {"$match": {"states.cities.id": city_id}},
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
