from fastapi import FastAPI, HTTPException, Query
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, Integer, Date
from datetime import date
from pydantic import BaseModel
import subprocess
import random
import string


app = FastAPI()


DB_CONNECTION = "mysql"
DB_HOST = "127.0.0.1"
DB_PORT = "3306"
DB_DATABASE = "XPanel_plus"
DB_USERNAME = "root"
DB_PASSWORD = ""




DATABASE_URL = f"{DB_CONNECTION}://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_DATABASE}"

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
    # username: str
    # password: str
    email: str = None
    mobile: str = None
    multiuser: int
    connection_start: int = None
    traffic: int
    expdate: date = None
    type_traffic: str = "mb"
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

    existing_usernames = db.query(Users.username).all()
    print("********")
    print(existing_usernames)

    used_numbers = {int(username.split("user")[1]) for (username,) in existing_usernames}
    print(used_numbers)
    new_username_number = 1
    while new_username_number in used_numbers:
        new_username_number += 1
    new_username = f"user{new_username_number}"
    
    new_username = "saeed"
    existing_user = db.query(Users).filter(Users.username == new_username).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="User Exists")

    else:

        random_password = "".join(random.choice(string.ascii_lowercase) for _ in range(4))



        traffic = 0

        if request.traffic > 0:
            traffic = request.traffic

        st_date = date.today() if not request.connection_start else None

        new_user = Users(
            username=new_username,
            password=random_password,
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

            db.add(new_user)
            db.commit()
            print("User added and changes committed successfully")

        except Exception as e:

            db.rollback()  # Rollback changes in case of an exception
            print("An error occurred:", str(e))

        new_traffic = Traffic(username=new_username, download='0', upload='0', total='0')
        db.add(new_traffic)
        db.commit()

        subprocess.run(["sudo", "adduser", "--disabled-password", "--gecos", "''", "--shell", "/usr/sbin/nologin", new_username])
        subprocess.run(["sudo", "passwd", new_username], input=f"{random_password}\n{random_password}\n", text=True, timeout=120)

        return None




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
            "host": "01.mtnssh.xyz",
            "port": 7777,
            "Udpgw port": 7302,
            "username": user.username,
            "password": user.password,
            "start_date": user.start_date,
            "end_date": user.end_date
        }
        user_list.append(user_data)

    return user_list
####

@app.get("/get_user_by_username")
async def get_user_by_username(username: str = Query(..., description="Username of the user to retrieve")):
    session = SessionLocal()
    try:
        user = session.query(Users).filter(Users.username == username).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        
        user_data = {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "start_date": user.start_date,
            "end_date": user.end_date,
            "status": user.status,
            "traffic": user.traffic,
            # ... (add other attributes you want to include)
        }

        return user_data
    finally:
        session.close()
