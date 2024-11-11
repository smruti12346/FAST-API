from fastapi import Depends, Header, HTTPException, Request
from starlette.middleware.base import BaseHTTPMiddleware
from pymongo import MongoClient


uri = "mongodb+srv://prabhucharanthetechnovate:pbJ76c9FKuSByMK1@cluster0.qagcixp.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
my_client = MongoClient(uri)
db = my_client["SHOPPINGEXPERTDB"]


class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        client_id = request.headers.get("x_client_id")
        request.state.db = get_client_database(client_id)
        response = await call_next(request)
        return response


def get_client_database(client_id: str):
    db_document = db["user"].find_one({"token": client_id})
    if db_document != None:
        db_documents = dict(db_document)
        new_client = MongoClient(db_documents['mongodb_connection_string'])
        return new_client[db_documents['db_name']]
    return None


async def get_client_id(x_client_id: str = Header(None)):
    if not x_client_id:
        raise HTTPException(status_code=400, detail="X-Client-ID header missing")
    return x_client_id