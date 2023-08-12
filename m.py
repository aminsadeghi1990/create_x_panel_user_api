from fastapi import FastAPI, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Date
from datetime import date
from pydantic import BaseModel
import subprocess

from peewee import DoesNotExist




# Define the FastAPI app
app = FastAPI()

DATABASE_URL = "sqlite:///test.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    email = Column(String)
    mobile = Column(String)
    multiuser = Column(Integer, nullable=False)
    start_date = Column(Date)
    end_date = Column(Date)
    date_one_connect = Column(Integer)
    customer_user = Column(String)
    status = Column(String)
    traffic = Column(Integer)
    referral = Column(String)
    desc = Column(String)


class Traffic(Base):
    __tablename__ = 'traffic'

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, nullable=False)
    download = Column(String)
    upload = Column(String)
    total = Column(String)

# Define models for request and response
class CreateUserRequest(BaseModel):
    token: str
    username: str
    password: str
    email: str = None
    mobile: str = None
    multiuser: int
    connection_start: int = None
    traffic: int
    expdate: date = None
    type_traffic: str
    desc: str = None

class CreateUserResponse(BaseModel):
    message: str





@app.on_event("startup")
async def startup():
    Base.metadata.create_all(bind=engine)

@app.on_event("shutdown")
async def shutdown():
    pass


@app.post("/add_user")
async def add_user(request: CreateUserRequest):
    db = SessionLocal()
    
    
    existing_user = db.query(Users).filter(Users.username == request.username).first()
    print("#####")
    print(existing_user)
    if existing_user:
        raise HTTPException(status_code=400, detail="User Exists")

    else:
        # Exception handling for existing user
        # Proceed to create a new user here
        traffic = 0

        if request.traffic > 0:
            traffic = request.traffic

        st_date = date.today() if not request.connection_start else None

        new_user = Users(
            username=request.username,
            password=request.password,
            email=request.email,
            mobile=request.mobile,
            multiuser=request.multiuser,
            start_date=st_date,
            end_date=request.expdate,
            date_one_connect=request.connection_start,
            customer_user='API',
            status='active',
            traffic=traffic,
            referral='',
            desc=request.desc
        )
        try:
            print("++++++")
            print(new_user)
            db.add(new_user)
            print("<><><><><><>")
            print(db.add(new_user))
            db.commit()
            print("User added and changes committed successfully")
        except Exception as e:
            db.rollback()  # Rollback changes in case of an exception
            print("An error occurred:", str(e))

        new_traffic = Traffic(username=request.username, download='0', upload='0', total='0')
        db.add(new_traffic)
        db.commit()

        subprocess.run(["sudo", "adduser", "--disabled-password", "--gecos", "''", "--shell", "/usr/sbin/nologin", request.username])
        subprocess.run(["sudo", "passwd", request.username], input=f"{request.password}\n{request.password}\n", text=True, timeout=120)

        return CreateUserResponse.message




@app.get("/get_all_users")
async def get_all_users():
    session = SessionLocal()
    users = session.query(Users).all()
    print("here is users")
    print(users)
    session.close()

    user_list = []

    for user in users:
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "start_date": user.start_date
        }
        user_list.append(user_data)

    return user_list
