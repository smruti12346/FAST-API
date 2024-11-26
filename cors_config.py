# cors_config.py
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://riverranch-api.shoppingxperts.com",
    "https://admin.riverranchdesigns.com",
    "https://riverranchdesigns.com",
    "https://www.riverranchdesigns.com",
    "https://thera-posture.com",
    "https://www.thera-posture.com",
]


def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )
