"""Coop stores scrapper."""
import os
from typing import Any, List, Optional

from dotenv import load_dotenv
from prefect import flow, task
from prefect.task_runners import ConcurrentTaskRunner
from scrappers.common import make_url, random_user_agents
from scrappers.repositories import save_to_document_store, save_to_json
from scrappers.utils import generate_flow_run_name
from tornado.escape import json_decode
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.httputil import HTTPHeaders

load_dotenv(os.path.join(os.getcwd(), ".env"))

BASE_URL = "https://proxy.api.coop.se/external/store/stores/map"


@task(name="Scrape Coop stores", tags=["coop", "stores"])
async def scrape_stores() -> Optional[List[Any]]:
    params = {"conceptIds": "12,6,95", "invertFilter": "true", "api-version": "v2"}
    headers = {
        "User-Agent": random_user_agents(),
        "Accept": "application/json",
        "Ocp-Apim-Subscription-Key": os.getenv("COOP_STORES_API_SUBSCRIPTION_KEY"),
    }
    url = BASE_URL
    request = HTTPRequest(url=make_url(url, params), headers=HTTPHeaders(headers))
    response = await AsyncHTTPClient().fetch(request)
    return json_decode(response.body)


@task(name="Save Coop stores data to JSON", tags=["coop", "stores"])
def save_stores_to_json(data):
    save_to_json(data, file_name="stores.json", brand="coop", category="stores")


@task(name="Save Coop stores data to document store", tags=["coop", "stores"])
async def save_stores_to_document_store(store):
    data = {"data": store}
    await save_to_document_store(
        data, brand="coop", category="stores", brand_id=store.get("storeId")
    )


@flow(
    name="Scrape Coop stores",
    flow_run_name=generate_flow_run_name,
    task_runner=ConcurrentTaskRunner(),
)
async def scrape_stores_flow():
    stores = await scrape_stores()
    save_stores_to_json(stores)
    await save_stores_to_document_store.map(stores)
