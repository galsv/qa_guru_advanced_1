from http import HTTPStatus
from fastapi import HTTPException
from sqlmodel import Session, select
from app.database.engine import engine
from app.models.user import User
from fastapi_pagination.ext.sqlmodel import paginate
from fastapi_pagination import Page


def get_user(user_id: int) -> User | None:
    with Session(engine) as session:
        return session.get(User, user_id)


def get_users() -> Page[User]:
    with Session(engine) as session:
        statement = select(User)
        return paginate(session, statement)


def create_user(user: User) -> User:
    with Session(engine) as session:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user


def update_user(user_id: int, user: User) -> User:
    with Session(engine) as session:
        statement = select(User).where(User.id == user_id)
        result = session.exec(statement)
        db_user = result.one()
        if not db_user:
            raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="User not found")

        db_user.email = user.email
        db_user.first_name = user.first_name
        db_user.last_name = user.last_name
        db_user.avatar = user.avatar

        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user


def delete_user(user_id: int):
    with Session(engine) as session:
        user = session.get(User, user_id)
        session.delete(user)
        session.commit()
