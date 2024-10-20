"""
If have more than one model to CRUD, create a base CRUD class and inherit -> Callisto(Geoengine)
Refer to generic user schema in callisto which has separate schemas for user creation, user update, user read, user delete
"""

from datetime import datetime

from aggregator.core.db import user_conn
from aggregator.schemas import User, UserCreate
from aggregator.utils.auth import get_password_hash


class CRUDUser:
    def create(self, user: UserCreate) -> User:
        user_data = user.dict()
        user_data["hashedPassword"] = get_password_hash(user.password)
        user_data["createdAt"] = datetime.now()
        user_data["updatedAt"] = datetime.now()
        user_data["isVerified"] = False
        user_data["disabled"] = False

        user_conn.insert_user(user_data)
        return User(**user_data)

    def read(self):
        pass

    def update(self):
        pass

    def delete(self):
        pass

    def get_by_email(self, email: str) -> User:
        user_data = user_conn.get_user_by_email(email)
        return User(**user_data)


user_crud = CRUDUser()
