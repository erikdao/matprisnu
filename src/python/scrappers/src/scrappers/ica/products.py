"""Scrapeprs for ICA's products."""
import json
import random
import time
from pathlib import Path
from typing import List

from data_models import IcaAPICategory, IcaAPIStore
from scrappers.common import USER_AGENTS, make_url
from scrappers.data_lake import AsyncDataLakeConnector
from scrappers.logger import sentry_logger as logger
from tornado import gen, queues
from tornado.escape import json_decode
from tornado.httpclient import AsyncHTTPClient

root_url = "https://handlaprivatkund.ica.se/stores/{accountNumber}/api/v5/products"
concurrency = 30


async def _scrape_func(url: str):
    """Get products data from ICA api.

    We only extract the `entities` attribute from the results returned
    by the API
    """
    AsyncHTTPClient.configure(
        None,
        max_clients=concurrency,
        defaults=dict(user_agent=random.choice(USER_AGENTS)),
    )
    response = await AsyncHTTPClient().fetch(url)

    data = json_decode(response.body)
    # Product is a dictionary whose keys are product's ids and values are product data
    return data.get("entities", {}).get("product")


def write_data_to_file(
    data: List[IcaAPICategory], storage_path: Path, file_name: str
) -> None:
    # Explicitly serialize data as the `json` package cannot automatically serialize CategorySchema
    serialized_data = [d.dict() for d in data]
    logger.info(f"Writing products of {len(serialized_data)} categories to file")
    with open(storage_path / file_name, "w") as f:
        json.dump(serialized_data, f)


async def persist_to_data_lake(data: IcaAPICategory, store: IcaAPIStore):
    products = data.products
    connector = AsyncDataLakeConnector()
    await connector.save_to_data_lake(
        collection_name="products",
        data=products,
        brand_name="ica",
        id_field="productId",
        brand_category=data.name,
        brand_category_id=data.id,
        ica_store_id=store.storeId,
        ica_store_account_number=store.accountNumber,
    )


async def scrapping_function(
    store: IcaAPIStore, categories: List[IcaAPICategory], storage_path: Path
):
    q = queues.Queue()
    start = time.time()
    fetching, fetched, dead = set(), set(), set()
    data = []

    async def scrape_products(current_url):
        if current_url in fetching:
            return
        fetching.add(current_url)

        scrapped_products = await _scrape_func(current_url)
        fetched.add(current_url)

        return scrapped_products

    async def worker():
        async for category in q:
            if category is None:
                return

            logger.debug(f"Scrapping products for category '{category}'")
            params = dict(category=category.id, limit=1000, offset=0)
            base_url = root_url.format(accountNumber=store.accountNumber)
            url = make_url(base_url, params)

            try:
                # Scrape products for this category
                scrapped_products = await scrape_products(url)
                products = [p for _, p in scrapped_products.items()]
                category.products = products
                await persist_to_data_lake(category, store)

                # Add the category (which contains all associated products) to the list of scrapped data
                data.append(category)
            except Exception as e:
                logger.error("Exception: %s %s" % (e, category.id))
                dead.add(url)
            finally:
                q.task_done()

    for cat in categories:
        await q.put(cat)

    workers = gen.multi([worker() for _ in range(concurrency)])
    await q.join()
    assert fetching == (fetched | dead)
    logger.info(
        "Done in %d seconds, scrapped %d categories" % (time.time() - start, len(data))
    )
    logger.info("Unable to scrape %s categories" % (len(dead)))

    # Signal all the workers to exit.
    for _ in range(concurrency):
        await q.put(None)
    await workers

    file_name = "%s__%s.json" % (store.storeId, store.accountNumber)
    write_data_to_file(data, storage_path, file_name)
