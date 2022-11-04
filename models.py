
from enum import unique
from operator import index
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from traitlets import default
from database import Base
from sqlalchemy_utils.types import ChoiceType
class Users(Base):
    __tablename__ = "users"

    STAFF_POSITION = (
        ('MANAGER', 'manager'),
        ('STAFF', 'staff'),
        ('EXECUTIVE MANAGER', 'executive manager')
    )
    
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String, nullable=True)
    position = Column(ChoiceType(choices=STAFF_POSITION),default="STAFF")

    orders = relationship('Orders', back_populates='users')


class Orders(Base):

    ORDER_STATUS = (
        ('PENDING', 'pending'),
        ('IN-TRANSIT', 'in-transit'),
        ('DELIVERED', 'delivered')
    )

    PIZZA_SIZES = (
        ('SMALL', 'small'),
        ('MEDIUM', 'medium'),
        ('LARGE', 'large'),
        ('EXTRA-LARGE', 'extra-large')
    )

    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=True)
    order_status = Column(ChoiceType(choices=ORDER_STATUS),default="PENDING")
    pizza_size = Column(ChoiceType(choices=PIZZA_SIZES),default="SMALL")
    user_id = Column(Integer, ForeignKey("users.id"))
    
    users = relationship('Users', back_populates='orders')



