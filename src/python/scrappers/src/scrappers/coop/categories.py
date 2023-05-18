"""Module to scrape product's Categories on Coop website.

It doesn't guarantee to be able to get all categories of products
provided by Coop as the website might be well-personalised to user's
session
"""
from typing import Any, List, Optional

from prefect import flow, task
from scrappers.common import random_user_agents
from scrappers.repositories import save_to_document_store, save_to_json
from scrappers.utils import generate_flow_run_name
from tornado.escape import json_decode
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.httputil import HTTPHeaders

BASE_URL = "https://www.coop.se/api/ecommerce/section/list"


async def scrape_categories() -> Optional[List[Any]]:
    headers = {
        "User-Agent": random_user_agents(),
        "Accept": "application/json",
    }

    url = BASE_URL

    request = HTTPRequest(url=url, headers=HTTPHeaders(headers))
    response = await AsyncHTTPClient().fetch(request)
    return json_decode(response.body)


@task(name="Save Coop categories data to JSON", tags=["coop", "categories"])
def save_categories_to_json(data):
    save_to_json(data, file_name="categories.json", brand="coop", category="categories")


@task(name="Save Coop categories data to document store", tags=["coop", "categories"])
async def save_categories_to_document_store(category):
    data = {"data": category}
    await save_to_document_store(
        data, brand="coop", category="categories", brand_id=category.get("id")
    )


@flow(name="Scrape Coop categories", flow_run_name=generate_flow_run_name)
async def scrape_categories_flow():
    categories = await scrape_categories()
    save_categories_to_json(categories)
    await save_categories_to_document_store.map(categories)
