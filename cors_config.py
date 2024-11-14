# cors_config.py
from fastapi.middleware.cors import CORSMiddleware

ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "https://ecomm-python-next.vercel.app",
    "https://python-next-ecommerce-frontend.vercel.app",
    "https://zvu.shoppingxperts.com",
    "https://riverranch-api.shoppingxperts.com",
    "https://thera-posture.com",
    "https://shoppingxpertsadmin-2va4z9vsk-digitalvates-projects.vercel.app",
]


def setup_cors(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE"],
        allow_headers=["Authorization", "Content-Type"],
    )
