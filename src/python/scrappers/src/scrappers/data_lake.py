"""Data Lake utilities."""
import os
from datetime import datetime
from typing import Any, Dict, List, Union

from dotenv import load_dotenv
from motor.motor_tornado import MotorClient, MotorCollection, MotorDatabase
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

load_dotenv(os.path.join(os.getcwd(), ".env"))


def build_conn_string() -> str:
    env = os.getenv("ENVIRONMENT")
    remote = True if env == "production" else False
    if not remote:
        username = os.getenv("DEV_MONGODB_USERNAME")
        password = os.getenv("DEV_MONGODB_PASSWORD")
        host = os.getenv("DEV_MONGODB_HOST")
        port = os.getenv("DEV_MONGODB_PORT")

        return f"mongodb://{username}:{password}@{host}:{port}/?authMechanism=DEFAULT"
    else:
        username = os.getenv("MONGODB_USERNAME")
        password = os.getenv("MONGODB_PASSWORD")
        cluster = os.getenv("MONGODB_CLUSTER")
        db = os.getenv("MONGODB_DATABASE")
        return f"mongodb+srv://{username}:{password}@{cluster}/{db}?tls=true&authSource=admin&replicaSet={db}"


def get_database(
    name: str = os.getenv("MONGODB_DATABASE"), atlas: bool = True
) -> Database:
    client = MongoClient(build_conn_string(atlas))
    return Database(client, name=name)


def get_collection(name: str, atlas: bool = True) -> Collection:
    db = get_database(atlas=atlas)
    return Collection(db, name=name)


def prepare_document(data: Any, brand_name: str, id_field: str, **kwargs):
    """Adds metadata to document, required fields are `brand_name` and
    `brand_id`"""
    metadata = {
        "brand_name": brand_name,
        "brand_id": data[id_field],
        "added_at": datetime.utcnow(),
    }
    if kwargs and len(kwargs.items()):
        metadata = {**metadata, **kwargs}

    document = {**metadata, "data": data}
    return document


def save_to_data_lake(
    collection_name: str,
    data: Union[List[Any], Dict[str, Any]],
    brand_name: str,
    id_field: str,
    **kwargs,
):
    """Augments the data and save them as documents in MongoDB's collection
    identified by `collection_name`"""
    collection = get_collection(collection_name, atlas=False)
    documents = []
    if isinstance(data, list):
        documents = [prepare_document(d, brand_name, id_field, **kwargs) for d in data]
    elif isinstance(data, dict):
        items = data.values()
        documents = [prepare_document(d, brand_name, id_field, **kwargs) for d in items]

    assert documents
    collection.insert_many(documents)


class DataLakeConnector:
    """A thin wrapper class for interacting with MongoDB data lake."""

    def __init__(self, database: str = None):
        self._database = database or os.getenv("MONGODB_DATABASE")
        self._client = MongoClient(build_conn_string())
        self._db = Database(self._client, name=self._database)

    def get_collection(self, name: str):
        return Collection(self._db, name=name)

    def save_to_data_lake(
        self,
        collection_name: str,
        data: Union[List[Any], Dict[str, Any]],
        brand_name: str,
        id_field: str,
        **kwargs,
    ):
        collection = self.get_collection(collection_name)
        if collection is None:
            return

        documents = []
        if isinstance(data, list):
            documents = [
                prepare_document(d, brand_name, id_field, **kwargs) for d in data
            ]
        elif isinstance(data, dict):
            items = data.values()
            documents = [
                prepare_document(d, brand_name, id_field, **kwargs) for d in items
            ]

        assert documents
        collection.insert_many(documents)


class AsyncDataLakeConnector:
    """A thin async wrapper class for interacting with MongoDB data lake."""

    def __init__(self, database: str = None, atlas: bool = True):
        self._database = database or os.getenv("MONGODB_DATABASE")
        self._client = MotorClient(build_conn_string())
        self._db = MotorDatabase(self._client, name=self._database)

    def get_collection(self, name: str):
        return MotorCollection(self._db, name=name)

    async def save_to_data_lake(
        self,
        collection_name: str,
        data: Union[List[Any], Dict[str, Any]],
        brand_name: str,
        id_field: str,
        **kwargs,
    ):
        collection = self.get_collection(collection_name)
        if collection is None:
            return

        documents = []
        if isinstance(data, list):
            documents = [
                prepare_document(d, brand_name, id_field, **kwargs) for d in data
            ]
        elif isinstance(data, dict):
            items = data.values()
            documents = [
                prepare_document(d, brand_name, id_field, **kwargs) for d in items
            ]

        assert documents
        await collection.insert_many(documents)
