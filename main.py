from fastapi import FastAPI
from auth_routers import auth_router
from order_routers import order_router
from fastapi_jwt_auth import AuthJWT
from schemas import Settings

app = FastAPI()

app.include_router(auth_router)
app.include_router(order_router)

