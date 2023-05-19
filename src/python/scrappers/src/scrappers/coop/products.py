"""Scrapeprs for Coop's products."""
import asyncio
import math
import os
from typing import Any, Dict, List, Optional, Tuple

from data_models.scrappers import CoopAPICategory
from loguru import logger
from scrappers.common import make_url, random_user_agents
from scrappers.repositories import bulk_save_to_document_store, save_to_json
from tornado.escape import json_decode, json_encode
from tornado.httpclient import AsyncHTTPClient, HTTPClientError, HTTPRequest
from tornado.httputil import HTTPHeaders

concurrency = 30
AsyncHTTPClient.configure(None, max_clients=concurrency)

BASE_URL = "https://external.api.coop.se/personalization/search/entities/by-attribute"
QUERY_PARAMS = {
    "api-version": "v1",
    "store": 251300,
    "groups": "CUSTOMER_PRIVATE",
    "device": "desktop",
    "direct": "false",
}
FACETS = [
    {
        "attributeName": "manufacturerName",
        "type": "distinct",
        "operator": "OR",
        "name": "brand",
        "selected": [],
    },
    {
        "attributeName": "filterLabels",
        "type": "distinct",
        "operator": "AND",
        "name": "environmentalLabels",
        "selected": [],
    },
    {
        "attributeName": "allergyFilters",
        "type": "distinct",
        "operator": "AND",
        "name": "allergyFilters",
        "selected": [],
    },
    {
        "attributeName": "nutritionFilters",
        "type": "distinct",
        "operator": "AND",
        "name": "nutritionFilters",
        "selected": [],
    },
    {
        "attributeName": "lifestyleFilters",
        "type": "distinct",
        "operator": "AND",
        "name": "lifestyleFilters",
        "selected": [],
    },
]
ITEMS_TAKE = 48


def _build_request_payload(
    category_id: Optional[str] = None, take: Optional[int] = 48, skip: Optional[int] = 0
) -> Dict[str, Any]:
    """Builds POST request payload for Coop's product API."""
    custom_data = {"consent": True}
    attribute = {"name": "categoryIds", "value": category_id}
    results_options = {"skip": skip, "take": take, "sortBy": [], "facets": FACETS}

    return {
        "attribute": attribute,
        "customData": custom_data,
        "resultsOptions": results_options,
    }


async def get_products_data(
    category_id: str, take: Optional[int] = ITEMS_TAKE, skip: Optional[int] = 0
) -> Optional[Tuple[int, Any]]:
    """Get products data from Coop by invoking a POST request to Coop's API."""
    # Build the request
    headers = {
        "User-Agent": random_user_agents(),
        "Content-Type": "application/json",
        "Accept": "application/json, text/plain, */*",
        "Ocp-Apim-Subscription-Key": os.getenv("COOP_PRODUCTS_API_SUBSCRIPTION_KEY"),
    }
    url = BASE_URL
    payload = _build_request_payload(category_id=category_id, take=take, skip=skip)

    request = HTTPRequest(
        url=make_url(url, QUERY_PARAMS),
        method="POST",
        headers=HTTPHeaders(headers),
        user_agent=headers["User-Agent"],
        body=json_encode(payload),
    )

    try:
        response = await AsyncHTTPClient().fetch(request)
        results = json_decode(response.body).get("results")
        return results["count"], results["items"]
    except HTTPClientError as e:
        logger.error(e)
        logger.debug(payload)
        raise e


async def scrape_products(category_id: str) -> List[Any]:
    """Scrapes all products for a given category."""
    items_take = ITEMS_TAKE
    items_skip = 0

    data = []
    items_count, page_items = await get_products_data(
        category_id=category_id, take=items_take, skip=items_skip
    )
    data.extend(page_items)

    total_pages = math.ceil(items_count / items_take)
    logger.debug(
        f"Category {category_id}; items_count = {items_count}; total_pages = {total_pages}"
    )

    if total_pages > 1:
        results = await asyncio.gather(
            *[
                get_products_data(
                    category_id=category_id, take=items_take, skip=page * items_take
                )
                for page in range(1, total_pages)
            ]
        )
        for idx, res in enumerate(results):
            data.extend(res[-1])
        logger.debug(f"Got {len(data)} products for category {category_id}")

    return data


def save_products_to_json(products, filename: str = "products.json"):
    save_to_json(products, file_name=filename, brand="coop", category="products")


async def save_products_to_document_store(products: List[Dict[str, Any]]) -> None:
    """Save product to Document Store."""
    data = []
    for product in products:
        data.append(
            {
                "data": product,
                "brand_id": product.get("id"),
                "brand": "coop",
                "category": "products",
            }
        )

    await bulk_save_to_document_store(data)


async def scrape_products_flow(category: CoopAPICategory) -> None:
    """Main scrapping function for aggregating category's products and write
    them to JSON files."""
    products = await scrape_products(category_id=str(category.id))

    if not len(products):
        return

    save_products_to_json(products, filename=f"{category.escapedName}.json")

    await save_products_to_document_store(products)
