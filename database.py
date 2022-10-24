
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


SQLALCHEMY_DATABASE_URL = "postgresql://postgres:240701@localhost/pizza_delivery"
engine = create_engine(SQLALCHEMY_DATABASE_URL)

#Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Create Base class
Base = declarative_base()

