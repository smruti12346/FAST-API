from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from fastapi.staticfiles import StaticFiles
from os import getcwd

from routes import userRoute, categoryRoute, productRoute, locationRoute, orderRoute, emailRoute , scriptsRoute, reportsRoute, shippingRoute

GOOGLE_CLIENT_ID = (
    "758479761027-k52ng36gkobmr9944mqcggtfun8c4si1.apps.googleusercontent.com"
)
GOOGLE_CLIENT_SECRET = "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"
GOOGLE_REDIRECT_URI = "http://127.0.0.1:8000/auth/google/callback"


app = FastAPI()
os.makedirs(getcwd() + "/uploads/", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ==================================================================================
# ============= Allow requests from localhost during development start =============
# ==================================================================================
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "https://ecomm-python-next.vercel.app",
        "https://python-next-ecommerce-frontend.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["Authorization", "Content-Type"],
)
# ==================================================================================
# ============= Allow requests from localhost during development end ===============
# ==================================================================================



# USER ROUTE START
app.include_router(userRoute.router)

# CATEGORY ROUTE START
app.include_router(categoryRoute.router)

# PRODUCT ROUTE START
app.include_router(productRoute.router)

# LOCATION ROUTE START
app.include_router(locationRoute.router)

# ORDER ROUTE START
app.include_router(orderRoute.router)

# EMAIL ROUTE START
app.include_router(emailRoute.router)

# REPORT ROUTE START
app.include_router(reportsRoute.router)

# REPORT ROUTE START
app.include_router(shippingRoute.router)

# SCRIPT ROUTE START
app.include_router(scriptsRoute.router)