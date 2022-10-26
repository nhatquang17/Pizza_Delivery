
from pyexpat import model
from unittest import result
from click import Choice
from django.db import router
from fastapi import APIRouter, Body, Request, Depends
from requests import delete
from sqlalchemy.sql.functions import mode
import models
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from auth_routers import get_current_user
from starlette.responses import RedirectResponse
from fastapi.responses import HTMLResponse
from starlette import status
from sqlalchemy_utils.types import ChoiceType

order_router = APIRouter(
    prefix="/orders",
    tags=['orders']
)

models.Base.metadata.create_all(bind=engine)

def get_db():
    try:
        db = SessionLocal()
        yield db
    except:
        db.close()

#GET ALL ORDERS OF A USER
@order_router.get("/")
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)

    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    #else:

    orders = db.query(models.Orders).filter(models.Orders.user_id == user.get("id")).all()

    return {"user": user}

#CREATE ORDER

@order_router.get("/add-order")
async def add_new_order(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth")
    #else:
    return {"Find user": "Authenticated user"}


@order_router.post("/add-order")
async def create_order(
    request: Request,
    quantity: int = None,
    order_status: str = None,
    pizza_size: str = None,
    db: Session = Depends(get_db)
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth")
    #esle:
    order_model = models.Orders()
    order_model.quantity = quantity
    order_model.order_status = order_status
    order_model.pizza_size = pizza_size
    order_model.user_id = user.get("id")

    db.add(order_model)
    db.commit()

    return {"Order status": "Completed"}


# UPDATE/EDIT OEDER
@order_router.get("/edit-order/{order_id}")
async def edit_order_commit(
    request: Request,
    order_id: int,
    db: Session = Depends(get_db)
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    #else:
    order = db.query(models.Orders).filter(models.Orders.id == order_id).first()

    return {"Find user": "Authenticated user"}

@order_router.post("/edit-order/{order_id}")
async def edit_order_commit(
    request: Request,
    order_id: int,
    quantity: int = None,
    order_status: str ="PENDING",
    pizza_size: str = "SMALL",
    db: Session = Depends(get_db)
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    #else:
    order_model = db.query(models.Orders).filter(models.Orders.id == order_id).first()

    order_model.quantity = quantity
    order_model.order_status = order_status
    order_model.pizza_size = pizza_size

    db.add(order_model)
    db.commit()

    return RedirectResponse(url="/orders", status_code=status.HTTP_302_FOUND)


# DELETE ORDER

@order_router.delete("/delete/{order_id}")
async def delete_order(
    request: Request,
    order_id: int,
    db: Session = Depends(get_db)
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    #else:

    order_model = db.query(models.Orders).filter(models.Orders.id == order_id)\
        .filter(models.Orders.user_id == user.get("id")).first()
    if not order_model:
        return {"Delete status": "Order_id doesn't exist"}
    #else:
    db.delete(order_model)
    db.commit()

    return {"Delete status": "Completed"}

@order_router.get("/complete/{order_id}")
async def complete_order(
    request: Request,
    order_id: int,
    db: Session = Depends(get_db)
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    order = db.query(models.Orders).filter(models.Orders.id == order_id).first()

    order.complete = not order.complete

    db.add(order)
    db.commit()

    return RedirectResponse(url="/orders", status_code=status.HTTP_302)


#Get all orders by User_id
@order_router.get("/all-order/{user_id}")
async def get_all_orders_by_user_id(
    request: Request,
    user_id: int,
    db: Session = Depends(get_db)
):  
    #Authen before get all orders by User_id
    user = await get_current_user(request)
    if user is None:
        return {"Find user": "user doesn't exist"}
    #else:

    user_inf = db.query(models.Orders).filter(models.Orders.user_id == user_id).all()

    if user_inf == []:
        return {"Find user": f" User_id {user_id} doesn't exist"}
    return {"All orders by user_id": user_inf}

#Get user by order_id
@order_router.get("/user-by-order_id/{order_id}")
async def get_user_by_order_id(
    request: Request,
    order_id: int,
    db: Session = Depends(get_db)
):
    #Authen before get user by order_id
    user = await get_current_user(request)
    if user is None:
        return {"Find user": "user doesn't exist"}
    #else:
    #get user_id (owner_id) in Orders table
    user_id = db.query(models.Orders).filter(models.Orders.id == order_id).first()

    #return username, id, email by user_id (find them in Users table by users ralationship)
    return {"username": user_id.users.username, "user_id": user_id.users.id, "user_email": user_id.users.email}

    #Note: user_id type: class, users is a attribute of this class
    #Note: user_id.users type class, username is a attribute of this class


#LIST ALL ORDERS MADE
@order_router.get("/all-orders-made")
async def list_all_orders_made(
    request: Request,
    db: Session = Depends(get_db)
):
    #Authen first
    user = await get_current_user(request)
    if user is None:
        return {"Find user": "User doesn't exist"}
    #else:
    all_orders = db.query(models.Orders).order_by(models.Orders.id).all()

    return {"All orders made": all_orders}

#LIST ALL ORDERS WHICH HAVE "X?" order_status
@order_router.get("/pending_status/{order_status}")
async def get_by_order_status(
    request: Request,
    order_status: str = None,
    db: Session = Depends(get_db)
):
    #Authen first
    user = await get_current_user(request)
    if user is None:
        return {"Find user": "User doesn't exist"}
    #else:
    result_by_order_status = db.query(models.Orders).filter(models.Orders.order_status == order_status).all()
    if result_by_order_status == []:
        return {"Result": f"{order_status} have no order"}
    #else:
    return {"All orders have PENDING status": result_by_order_status}
