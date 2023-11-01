from contextlib import asynccontextmanager
from typing import Optional

from beanie import Document, init_beanie
from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient

client = AsyncIOMotorClient(
    "mongodb+srv://myDatabaseUser:D1fficultP2ssw0rd@cluster0.example.mongodb.net/?retryWrites=true&w=majority"
)


class User(Document):
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None


async def fetch_user(username: str) -> User:
    result = await User.find_one(User.username == username)
    if result is None:
        raise HTTPException(status_code=404, detail="User not found")
    return result


async def init_db():
    await init_beanie(database=client.database_name, document_models=[User])


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/users/", response_model=User)
async def create_user(user: User):
    """
    Insert a new user record.
    """
    try:
        await user.insert()
        return user
    except Exception as e:
        raise e


@app.get("/users/{username}", response_model=User)
async def get_user(username: str):
    """
    Fetch a user using a given username.

    Args:
        username: the username of an existing user.

    Raises a 404 not found exception if the username does not match any user.
    """
    try:
        user = await fetch_user(username)
        return user
    except Exception as e:
        raise e
