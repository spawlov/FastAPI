from databases import Database
from fastapi import FastAPI, HTTPException
from fastapi.concurrency import asynccontextmanager
from pydantic import BaseModel, EmailStr
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = "sqlite:///./tets.db"

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)



class UserInDB(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String)


Base.metadata.create_all(bind=engine)


class User(BaseModel):
    username: str
    email: EmailStr

class UserResponse(BaseModel):
    id:int
    username:str
    email:EmailStr


@asynccontextmanager
async def lifespan(app: FastAPI):
    await database.connect()
    yield
    await database.disconnect()

app = FastAPI(lifespan=lifespan)
database = Database(DATABASE_URL)

@app.post("/register", response_model=User)
async def register_user(user: User) -> User:
    query = UserInDB.__table__.select().where(UserInDB.username == user.username)
    db_user = await database.fetch_one(query)
    if db_user:
        raise HTTPException(status_code=400, detail="User already registered")
    
    query = UserInDB.__table__.insert().values(username=user.username, email=user.email)
    await database.execute(query)
    return user

@app.get("/user/{username}", response_model=UserResponse)
async def get_user(username: str):
    query = UserInDB.__table__.select().where(UserInDB.username == username)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.delete("/user/{username}", response_model=dict)
async def delete_user(username: str):
    query = UserInDB.__table__.select().where(UserInDB.username == username)
    user = await database.fetch_one(query)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    query = UserInDB.__table__.delete().where(UserInDB.username == username)
    await database.execute(query)
    return {"detail": "User deleted"}