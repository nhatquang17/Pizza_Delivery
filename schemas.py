from typing import List, Union
from pydantic import BaseModel

class SignUpModel(BaseModel):
    id: Union[int, None] = None
    username: str
    email: str
    password: str
    is_active: Union[bool,None]
    is_staff: Union[bool,None]

    class Config():
        orm_mode = True
        schema_extra = {
            'example': {
                "username": "John",
                "email": "johncreate@gmail.com",
                "password":"thisisafakepass",
                "is_active": False,
                "is_staff": True
            }
        }

class Settings(BaseModel):
    authjwt_secret_key: str = 'cfe35b1d51cb70bff29039255224395248e59211aec3d0361fde88f1772fb3c3'

class LoginModel(BaseModel):
    username: str
    password: str