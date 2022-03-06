import typing
import uuid

import motor.motor_asyncio
from pydantic import UUID4, BaseModel, Field

from config import settings


class DatabaseWrapper:
    __client = None
    __db = None
    __projects_collection = None
    __project_credentials_collection = None
    __project_deploy_collection = None
    __loop = None

    @classmethod
    def set_event_loop(cls, loop):
        cls.__loop = loop

    @classmethod
    def get_client(cls):
        if cls.__client is None:
            cls.__client = motor.motor_asyncio.AsyncIOMotorClient(
                settings.database_url, uuidRepresentation="standard", io_loop=cls.__loop
            )
        return cls.__client

    @classmethod
    def get_db(cls):
        if cls.__db is None:
            client = cls.get_client()
            cls.__db = client[settings.database_name]
        return cls.__db

    @classmethod
    def get_projects_collection(cls):
        if cls.__projects_collection is None:
            db = cls.get_db()
            cls.__projects_collection = db["projects"]
        return cls.__projects_collection

    @classmethod
    def get_project_credentials_collection(cls):
        if cls.__project_credentials_collection is None:
            db = cls.get_db()
            cls.__project_credentials_collection = db["project_credentials"]
        return cls.__project_credentials_collection

    @classmethod
    def get_project_deploy_collection(cls):
        if cls.__project_deploy_collection is None:
            db = cls.get_db()
            cls.__project_deploy_collection = db["project_deploy"]
        return cls.__project_deploy_collection


class BaseDBModel(BaseModel):
    created_by: UUID4
    id: UUID4 = Field(default_factory=uuid.uuid4)


BDBM = typing.TypeVar("BDBM", bound=BaseDBModel)


class MongoDatabase(typing.Generic[BDBM]):
    """Database adapter for MongoDB"""

    collection: motor.motor_asyncio.AsyncIOMotorCollection

    def __init__(
        self,
        db_model: typing.Type[BDBM],
        collection: motor.motor_asyncio.AsyncIOMotorClient,
    ):
        self.db_model = db_model
        self.collection = collection
        self.collection.create_index("id", unique=True)

    async def get(self, id: UUID4) -> typing.Optional[BDBM]:
        db_object = await self.collection.find_one({"id": id})
        return self.db_model(**db_object) if db_object else None

    async def filter(self, filter_params: dict) -> list[BDBM]:
        result = []
        async for db_object in self.collection.find(filter_params):
            result.append(self.db_model(**db_object))
        return result

    async def create(self, db_object: BDBM) -> BDBM:
        await self.collection.insert_one(db_object.dict())
        return db_object

    async def update(self, db_object: BDBM) -> BDBM:
        await self.collection.replace_one({"id": db_object.id}, db_object.dict())
        return db_object

    async def delete(self, db_object) -> None:
        await self.collection.delete_one({"id": db_object.id})


def get_project_collection():
    return DatabaseWrapper.get_projects_collection()


def get_project_credentials_collection():
    return DatabaseWrapper.get_project_credentials_collection()


def get_project_deploy_collection():
    return DatabaseWrapper.get_project_deploy_collection()
