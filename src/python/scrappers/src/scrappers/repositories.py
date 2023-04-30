"""Repository module that defines how to store and retrieve documents from different storage backends."""
import os
from abc import ABC, abstractmethod
import json
from uuid import uuid4

import boto3
import couchdb
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


class CouchDBRepository(DocumentRepository):
    """Repository that stores documents in CouchDB."""

    def __init__(self, database, host="localhost", port=5984):
        super().__init__()

        self._database = database
        self._host = host
        self._port = port
        self._couch = self._init_client()
        self._db = self._couch[self._database]

    def _init_client(self):
        username = os.getenv("COUCHDB_USERNAME")
        password = os.getenv("COUCHDB_PASSWORD")
        conn_str = f"http://{username}:{password}@{self._host}:{self._port}"
        return couchdb.Server(conn_str)

    def _gen_id(self):
        return str(uuid4().hex)

    def save_document(self, document):
        pass


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
        if isinstance(document, dict):
            document = json.dumps(document)
        self._bucket.put_object(Key=path, Body=document)
