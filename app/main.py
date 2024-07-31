import dotenv
import uvicorn
import logging
from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.routers import status, users
from app.database.engine import create_db_and_tables
from fastapi_pagination import add_pagination

dotenv.load_dotenv()


@asynccontextmanager
async def lifespan(_: FastAPI):
    logging.warning("On startup")
    create_db_and_tables()
    yield
    logging.warning("On shutdown")

app = FastAPI()
add_pagination(app)
app.include_router(status.router)
app.include_router(users.router)


if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8002)
