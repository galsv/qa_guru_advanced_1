from pydantic import BaseModel, EmailStr, HttpUrl


class User(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    avatar: HttpUrl
