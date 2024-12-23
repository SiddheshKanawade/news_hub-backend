"""
If have more than one model to CRUD, create a base CRUD class and inherit -> Callisto(Geoengine)
Refer to generic user schema in callisto which has separate schemas for user creation, user update, user read, user delete
"""

from datetime import datetime

from aggregator.core.db import db_conn
from aggregator.schemas import User, UserCreate, UserInDB
from aggregator.utils.auth import get_password_hash


class CRUDUser:
    def create(self, user: UserCreate) -> UserInDB:
        user_data = user.dict()
        user_data["hashedPassword"] = get_password_hash(user.password)
        user_data["createdAt"] = datetime.now()
        user_data["updatedAt"] = datetime.now()
        user_data["isVerified"] = False
        user_data["disabled"] = False

        user = User(**user_data)
        db_conn.insert_user(UserInDB(**user_data))
        return user

    def read(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass

    def get_by_email(self, email: str) -> User:
        user_data = db_conn.get_user_by_email(email)
        if not user_data:
            return None
        return User(**user_data)

    def add_feed_sources(self, email: str, sources: list[str]):
        return db_conn.add_feed_sources(email, sources)


user_crud = CRUDUser()
