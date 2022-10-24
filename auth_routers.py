
import sys
sys.path.append("..")

from starlette.responses import RedirectResponse

from fastapi import Depends, HTTPException, status, APIRouter, Request, Response, Form
from pydantic import BaseModel
from typing import Optional
import models
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from datetime import datetime, timedelta
from jose import ExpiredSignatureError, jwt, JWTError

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Union

reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/login",
    scheme_name="JWT"
)

SECRET_KEY = "KlgH6AzYDeZeGwD288to79I3vTHT8wp7"
ALGORITHM = "HS256"

bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

models.Base.metadata.create_all(bind=engine)

oauth2_bearer = OAuth2PasswordBearer(tokenUrl="token")

auth_router = APIRouter(
    prefix="/auth",
    tags=["auth"],
    responses={401: {"user": "Not authorized"}}
)

class TokenData(BaseModel):
    username: Union[str, None] = None

class LoginForm:
    def __init__(self, request: Request):
        self.request: Request = request
        self.username: Optional[str] = None
        self.password: Optional[str] = None

    async def create_oauth_form(self):
        form = await self.request.form()
        self.username = form.get("email")
        self.password = form.get("password")
    
def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()
    
def get_password_hash(password):
    return bcrypt_context.hash(password)

def verify_password(plain_password, hassed_password):
    return bcrypt_context.verify(plain_password, hassed_password)

def authenticate_user(username: str, password: str, db):
    user = db.query(models.Users).filter(models.Users.username == username).first()

    if not user: # user doesn't exist
        return False
    if not verify_password(password, user.password): #Incorrect password
        return False
    #else:
    return user     #username and password are correct


def create_access_token(username: str, user_id: int, expires_delta: Optional[timedelta]= None):
    encode = {"sub": username, "id": user_id}
    if expires_delta: 
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    encode.update({"exp": expire})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


async def get_current_user(request: Request):
    try:
        token = request.cookies.get("access_token")
        if token is None:
            return None
        #else:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        user_id: int = payload.get("id")

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User doesn't exist")
        #else:
        return {"username": username, "id": user_id}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Not found")


@auth_router.post("/token")
async def login_for_access_token(
    response: Response, 
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    #else:
    token_expires = timedelta(minutes=60)
    token = create_access_token(user.username, user.id, expires_delta=token_expires)

    response.set_cookie(key="access_token", value=token, httponly=True)
    return {"access_token": token, "token_type": "bearer"}

@auth_router.post("/")
async def login(request: Request, db: Session = Depends(get_db)):
    try:
        form = LoginForm(request)
        await form.create_oauth_form()
        response = RedirectResponse(url="/orders", status_code=status.HTTP_302_FOUND)

        validate_user_cookie = await login_for_access_token(response=response, form_data=form, db=db)
        
        if not validate_user_cookie: #validate_user_cookie = False
            return {"Login status": "Incorrect Username or Password!"}
        #else:
        return response #Điều hướng qua trang order
    except:
        return {"Login status": "Unknown Error"}


@auth_router.post("/register")
async def register_user(
    request: Request,
    email: str = Form(...),
    username: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    #user validate
    validate1 = db.query(models.Users).filter(models.Users.username == username).first()
    #email validate
    validate2 = db.query(models.Users).filter(models.Users.email == email).first()

    if validate1 is not None or validate2 is not None:
        return {"Register status": "Username or email already exist!"}
    #else

    user_model = models.Users()
    user_model.username = username
    user_model.email = email
    
    hash_password = get_password_hash(password)
    user_model.password = hash_password
    user_model.is_active = False
    user_model.is_staff = False

    #Save into db
    db.add(user_model)
    db.commit()
    
    return {"Register status": "User successfully created"}
