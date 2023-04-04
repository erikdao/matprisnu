"""ICA Stores scrapper."""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

from scrappers.common import make_url
from scrappers.data_lake import AsyncDataLakeConnector
from scrappers.logger import sentry_logger as logger
from tornado.escape import json_decode
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from tornado.httputil import HTTPHeaders

STORES_URL = "https://apimgw-pub.ica.se/sverige/digx/mdsastoresearch/v1/stores/"


async def _scrape_func(
    url: str, headers: Optional[Dict[str, Any]], params: Optional[Dict[str, Any]]
):
    request = HTTPRequest(
        url=make_url(url, params), method="GET", headers=HTTPHeaders(headers)
    )
    response = await AsyncHTTPClient().fetch(request)
    return json_decode(response.body)


async def scrapping_function(storage_path: Path, **kwargs):
    headers = {"Authorization": f"Bearer {os.getenv('ICA_AUTH_TOKEN')}"}
    # ICA currently has around 1300 stores across Sweden. Their API pagination is set to 20
    # We've seen that the API allows to retrieve all stores data at once by setting a larger `take`
    params = {
        "offset": 0,
        "take": 1500,
        "sort": "storeName",
        "urbanArea": "",
        "district": "",
    }
    stores = await _scrape_func(url=STORES_URL, headers=headers, params=params)

    json_path = storage_path / "stores.json"
    logger.debug(f"Writing {len(stores)} store items to {json_path}")
    with open(json_path, "w") as f:
        json.dump(stores, f, indent=2)

    logger.debug("Saving scrapped stores to data lake")
    connector = AsyncDataLakeConnector()
    await connector.save_to_data_lake(
        collection_name="stores",
        data=stores,
        brand_name="ica",
        id_field="storeId",
    )
