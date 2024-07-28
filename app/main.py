import dotenv
import uvicorn
from fastapi import FastAPI

from routers import status, users
from app.database.engine import create_db_and_tables
from fastapi_pagination import add_pagination

dotenv.load_dotenv()
app = FastAPI()
app.include_router(status.router)
app.include_router(users.router)


if __name__ == "__main__":
    create_db_and_tables()
    add_pagination(app)
    uvicorn.run(app, host="localhost", port=8002)
