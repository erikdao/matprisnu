"""Repository module that defines how to store and retrieve documents from
different storage backends."""
import json
import os
from abc import ABC, abstractmethod
from datetime import datetime
from uuid import uuid4
from pathlib import Path
from typing import Any, Dict

import boto3
from aiocouch import CouchDB
from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())


class DocumentRepository:
    """Abstract repository that defines how to store and retrieve documents
    from different storage backend."""

    __metaclass__ = ABC

    @abstractmethod
    def save_document(self, document):
        """Save a document to the repository."""
        pass


class JSONRepository:
    """Repository that stores documents in JSON files."""

    def __init__(self, storage_path):
        super().__init__()

        self._storage_path = storage_path

    @property
    def storage_path(self):
        return self._storage_path

    def save_document(self, document, path):
        with open(path, "w") as f:
            json.dump(document, f, indent=2)


class AsyncDocumentRepository:
    """Abstract repository that defines how to store and retrieve documents
    from different storage backend."""

    __metaclass__ = ABC

    @abstractmethod
    async def save_document(self, document):
        """Save a document to the repository."""
        pass


def _get_couchdb_url() -> str:
    username = os.getenv("COUCHDB_USERNAME")
    password = os.getenv("COUCHDB_PASSWORD")
    host = os.getenv("COUCHDB_HOST")
    port = os.getenv("COUCHDB_PORT")
    return f"http://{username}:{password}@{host}:{port}"


def couchdb_context(func):
    async def wrapper(*args, **kwargs):
        async with CouchDB(_get_couchdb_url()) as couch:
            db = await couch[os.getenv("COUCHDB_DATABASE")]
            return await func(db, *args, **kwargs)

    return wrapper


class CouchDBRepository(AsyncDocumentRepository):
    """Repository that stores documents in CouchDB."""

    def __init__(self):
        super().__init__()

    def _gen_id(self):
        return str(uuid4().hex)

    def _decorate_document(self, document):
        document["_id"] = self._gen_id()
        # Since we only append new document to the database, we don't actually
        # need to update the document's updated_at field.
        document["updated_at"] = datetime.utcnow().isoformat()

    @couchdb_context
    async def save_data(self, db, data):
        self._decorate_document(data)
        doc = db.create(data["_id"], data=data)
        return await doc.save()


class CloudFlareR2Repository(DocumentRepository):
    """Repository that stores documents in CloudFlare R2 storage."""

    def __init__(self):
        super().__init__()

        self._s3 = self._init_client()
        self._bucket = self._s3.Bucket(os.getenv("CLOUDFLARE_R2_BUCKET_NAME"))

    def _init_client(self):
        endpoint = (
            f"https://{os.getenv('CLOUDFLARE_R2_ACCOUNT_ID')}.r2.cloudflarestorage.com"
        )
        return boto3.resource(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=os.getenv("CLOUDFLARE_R2_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("CLOUDFLARE_R2_SECRET_ACCESS_KEY"),
        )

    def save_document(self, document, path):
        if not isinstance(document, (bytes, bytearray)):
            # S3 put_object requires a bytes-like object
            document = json.dumps(document)

        self._bucket.put_object(Key=path, Body=document)


def get_scrapper_respository(format: str):
    """Return a repository based on the format."""
    if format == "json":
        return JSONRepository(storage_path=Path(os.getenv("SCRAPPER_BASE_STORAGE_PATH")))
    elif format == "couchdb":
        return CouchDBRepository
    elif format == "cloudflare-r2":
        return CloudFlareR2Repository
    else:
        raise ValueError(f"Unsupported format {format}")
    

def save_to_json(data: Dict[str, Any], file_name: str, brand: str, category: str, create_date_dir: bool = True):
    """Save scrapped data to JSON file."""
    repo = get_scrapper_respository(format="json")
    if create_date_dir:
        path = repo.storage_path / brand / datetime.now().strftime("%Y-%m-%d") / category / file_name
    else:
        path = repo.storage_path / brand / category / file_name

    repo.save_document(data, path)
