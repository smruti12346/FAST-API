from db import db

collection = db["location"]


def get_all_country(request):
    try:
        result = collection.find({"deleted_at": None}, {"currency": 1, "iso2": 1, "name": 1, "id": 1, "_id": 1})
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_states_by_country(country_code):
    try:
        pipeline = [
            {"$match": {"iso2": country_code}},
            {"$unwind": "$states"},
            {"$project": {"_id": 0, "id": "$states.id", "name": "$states.name", "state_code": "$states.state_code"}},
        ]
        result = list(db.location.aggregate(pipeline))
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_city_by_country_and_state(country_code, state_code):
    try:
        pipeline = [
            {"$match": {"iso2": country_code}},
            {"$unwind": "$states"},
            {"$match": {"states.state_code": state_code}},
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

def get_country_by_id(country_code: int):
    try:
        result = collection.find({"deleted_at": None, "id": country_code}, {"name": 1, "id": 1, "_id": 1, "iso2": 1})
        data = []
        for doc in result:
            doc["_id"] = str(doc["_id"])
            data.append(doc)
        return {"data": data, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_states_by_state_code_and_country_code(country_code : int, state_code : int):
    try:
        pipeline = [
            {"$match": {"id": country_code}},
            {"$unwind": "$states"},
            {"$match": {"states.id": state_code}},
            {"$project": {"_id": 0, "id": "$states.id", "name": "$states.name", "state_code": "$states.state_code"}},
        ]
        result = list(db.location.aggregate(pipeline))
        return {"data": result, "status": "success"}
    except Exception as e:
        return {"message": str(e), "status": "error"}


def get_city_by_city_id_country_code_and_state_code(country_code, state_code, city_id):
    try:
        pipeline = [
            {"$match": {"id": country_code}},
            {"$unwind": "$states"},
            {"$match": {"states.id": state_code}},
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
