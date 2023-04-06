"""Scrapping tasks."""
import asyncio
import importlib
import json
from datetime import datetime
from pathlib import Path
from typing import Any, List

import luigi
from data_models import CoopAPICategory, IcaAPICategory, IcaAPIStore


def today() -> str:
    return datetime.utcnow().strftime("%Y%m%d")


class ScrappingTask(luigi.Task):
    brand = luigi.Parameter()
    output_path = luigi.Parameter(
        description="Path to directory where output data will be stored"
    )

    @property
    def brand_name(self) -> str:
        return str(self.brand)

    @property
    def common_output_dir(self) -> Path:
        return Path(str(self.output_path)) / self.brand_name / today()

    def setup_storage_path(self, dir_name: str) -> Path:
        """Create directory to hold the scrapped data for particular object
        group."""
        data_path = self.common_output_dir / dir_name
        data_path.resolve()
        data_path.mkdir(parents=True, exist_ok=True)

        return data_path


class CoopTask(ScrappingTask):
    brand = luigi.Parameter(default="coop")


class CoopStoreScrappingTask(CoopTask):
    """Task to scrape stores from Coop."""

    def run(self):
        from scrappers.coop.stores import scrapping_function

        storage_path = self.setup_storage_path("stores")

        loop = asyncio.get_event_loop()
        loop.run_until_complete(scrapping_function(storage_path))

    def output(self):
        return luigi.LocalTarget(f"{self.common_output_dir}/stores/stores.json")


class CoopCategoryScrappingTask(CoopTask):
    """Task to scrape categories from Coop."""

    def run(self):
        from scrappers.coop.categories import scrapping_function

        storage_path = self.setup_storage_path("categories")

        loop = asyncio.get_event_loop()
        loop.run_until_complete(scrapping_function(storage_path))

    def output(self):
        return luigi.LocalTarget(f"{self.common_output_dir}/categories/categories.json")


class CoopCategoryProductScrappingTask(CoopTask):
    """Task to scrape app products for a given category."""

    category_dict = luigi.DictParameter(
        description="Dictionary containing category data"
    )

    @property
    def category(self) -> CoopAPICategory:
        return CoopAPICategory.parse_obj(self.category_dict)

    def run(self):
        from scrappers.coop.products import scrapping_function

        storage_path = self.setup_storage_path("products")

        loop = asyncio.get_event_loop()
        loop.run_until_complete(scrapping_function(self.category, storage_path))

    def output(self):
        return luigi.LocalTarget(
            f"{self.common_output_dir}/products/{self.category.escapedName}.json"
        )


class CoopProductsScrappingTask(CoopTask, luigi.WrapperTask):
    """Task to scrape all products from Coop."""

    def requires(self):
        return CoopCategoryScrappingTask(output_path=self.output_path)

    def run(self):
        from scrappers.coop.categories import get_categories_from_file

        # Get the path of category file from the output of `CoopCategoryScrappingTask`
        category_file = self.input().path
        categories = get_categories_from_file(category_file, level=1)

        for cat in categories:
            yield CoopCategoryProductScrappingTask(
                output_path=self.output_path, category_dict=cat.dict()
            )


class CoopScrappingTask(CoopTask, luigi.WrapperTask):
    """Wrapper scrapping task for Coop.

    It sequentially calls the store scrapping task, then the products
    scrapping task which requires the categories scrapping task to be
    finished.
    """

    def requires(self):
        return [
            CoopStoreScrappingTask(output_path=self.output_path),
            CoopProductsScrappingTask(output_path=self.output_path),
        ]


class AxfoodTask(ScrappingTask):
    """Common scrapping task for Hemköp and Willys."""

    brand = luigi.Parameter()

    def get_scrapping_function(self, for_module: str):
        module = importlib.import_module(f"scrapper.axfood.{for_module}")
        return getattr(module, "scrapping_function")


class AxfoodStoreScrappingTask(AxfoodTask):
    """Task to scrape stores from Axfood API."""

    def run(self):
        scrapping_function = self.get_scrapping_function("stores")

        storage_path = self.setup_storage_path("stores")

        loop = asyncio.get_event_loop()
        loop.run_until_complete(scrapping_function(storage_path))

    def output(self):
        return luigi.LocalTarget(f"{self.common_output_dir}/stores/stores.json")


class AxfoodCategoryScrappingTask(AxfoodTask):
    """Task to scrape categories from Axfood API."""

    def run(self):
        scrapping_function = self.get_scrapping_function("categories")

        storage_path = self.setup_storage_path("categories")

        loop = asyncio.get_event_loop()
        loop.run_until_complete(scrapping_function(storage_path))

    def output(self):
        return luigi.LocalTarget(f"{self.common_output_dir}/categories/categories.json")


class AxfoodCategoryProductScrappingTask(AxfoodTask):
    """Task to scrape app products for a given category."""

    category = luigi.Parameter(description="Category (url) to be scrapped")

    def run(self):
        scrapping_function = self.get_scrapping_function("products")

        storage_path = self.setup_storage_path("products")

        loop = asyncio.get_event_loop()
        loop.run_until_complete(scrapping_function(str(self.category), storage_path))

    def output(self):
        return luigi.LocalTarget(
            f"{self.common_output_dir}/products/{self.category}.json"
        )


class AxfoodProductsScrappingTask(AxfoodTask, luigi.WrapperTask):
    """Task to scrape all products from Axfood API."""

    def requires(self):
        return AxfoodCategoryScrappingTask(
            brand=self.brand, output_path=self.output_path
        )

    def run(self):
        # Get the path of category file from the output of `HWCategoryScrappingTask`
        category_file = self.input().path
        categories = self.get_categories(category_file)

        for category in categories:
            yield AxfoodCategoryProductScrappingTask(
                brand=self.brand, category=category, output_path=self.output_path
            )

    @staticmethod
    def get_categories(file: str) -> List[str]:
        """Get categories from file.

        Returns only top-level categories
        """
        with open(file, "r") as f:
            data = json.load(f)
        return [d["url"] for d in data]


class AxfoodScrappingTask(AxfoodTask, luigi.WrapperTask):
    def requires(self):
        return [
            AxfoodStoreScrappingTask(brand=self.brand, output_path=self.output_path),
            AxfoodProductsScrappingTask(brand=self.brand, output_path=self.output_path),
        ]


class IcaTask(ScrappingTask):
    brand = luigi.Parameter(default="ica")


class IcaStoreScrappingTask(IcaTask):
    """Task to scrape stores from Ica."""

    def run(self):
        from scrappers.ica.stores import scrapping_function

        storage_path = self.setup_storage_path("stores")

        loop = asyncio.get_event_loop()
        loop.run_until_complete(scrapping_function(storage_path))

    def output(self):
        return luigi.LocalTarget(f"{self.common_output_dir}/stores/stores.json")


class IcaScrapeCategoriesForStoreTask(IcaTask):
    """Task to scrape categories for each store from ICA."""

    store_id = luigi.Parameter(
        description="Id of the store which the scrapper will scrape categories"
    )

    def requires(self):
        return IcaStoreScrappingTask(brand=self.brand, output_path=self.output_path)

    def run(self):
        from scrappers.ica.categories import scrapping_function

        storage_path = self.setup_storage_path("categories")

        stores_file = self.input().path

        store = self.get_store(stores_file, self.store_id)

        loop = asyncio.get_event_loop()
        loop.run_until_complete(scrapping_function(store, storage_path))

    def output(self):
        return luigi.LocalTarget(
            f"{self.common_output_dir}/categories/{self.store_id}_categories.json"
        )

    @staticmethod
    def get_store(file: str, store_id: Any) -> IcaAPIStore:
        with open(file, "r") as f:
            stores = json.load(f)

        store = [s for s in stores if s["storeId"] == store_id][0]
        return IcaAPIStore.parse_obj(store)


class IcaStoresCategoriesScrappingTask(IcaTask, luigi.WrapperTask):
    """Wrapper task to scrape categories for all stores from ICA."""

    def requires(self):
        return IcaStoreScrappingTask(brand=self.brand, output_path=self.output_path)

    def run(self):
        # Get the path of category file from the output of `IcaStoreScrappingTask`
        stores_file = self.input().path

        stores = self.get_stores(stores_file)
        for store in stores:
            yield IcaScrapeCategoriesForStoreTask(
                brand=self.brand, output_path=self.output_path, store_id=store.storeId
            )

    def output(self):
        return luigi.LocalTarget(f"{self.common_output_dir}/categories")

    @staticmethod
    def get_stores(file: str) -> List[IcaAPIStore]:
        with open(file, "r") as f:
            data = json.load(f)
        stores = [s for s in data if s["onlinePlatform"] == "OSP"]
        return [IcaAPIStore.parse_obj(item) for item in stores]


class IcaScrapeProductsForStoreTask(IcaTask):
    store_dict = luigi.DictParameter(description="Dictionary of format IcaAPIStore")
    category_file = luigi.Parameter(
        description="JSON file containing categories for this store"
    )

    @property
    def store(self) -> IcaAPIStore:
        return IcaAPIStore.parse_obj(self.store_dict)

    @property
    def categories(self) -> List[IcaAPICategory]:
        with open(str(self.category_file), "r") as f:
            data = json.load(f)
            # Only get the lowest level categories
            data = {k: v for k, v in data.items() if len(v["children"]) == 0}
        return [IcaAPICategory.parse_obj(d) for _, d in data.items()]

    def run(self):
        from scrappers.ica.products import scrapping_function

        storage_path = self.setup_storage_path("products")

        loop = asyncio.get_event_loop()
        loop.run_until_complete(
            scrapping_function(self.store, self.categories, storage_path)
        )

    def output(self):
        return luigi.LocalTarget(
            f"{self.common_output_dir}/products/{self.store.storeId}__{self.store.accountNumber}.json"
        )


class IcaScrappingTask(IcaTask, luigi.WrapperTask):
    """Wrapper task to scrape data from ICA First, the stores and their
    categories are scraped.

    Then, products from each store are scraped.
    """

    def requires(self):
        return IcaStoresCategoriesScrappingTask(
            brand=self.brand, output_path=self.output_path
        )

    def run(self):
        categories_dir = Path(self.input().path).resolve()
        ica_today_dir = categories_dir.parent
        stores_dir = ica_today_dir / "stores"

        stores = self.get_stores(stores_dir / "stores.json")
        for store in stores:
            store_dict = store.dict()
            category_file = str(categories_dir / f"{store.storeId}_categories.json")
            yield IcaScrapeProductsForStoreTask(
                brand=self.brand,
                output_path=self.output_path,
                store_dict=store_dict,
                category_file=category_file,
            )

    @staticmethod
    def get_stores(file: Path) -> List[IcaAPIStore]:
        """Read all stores from file."""
        with open(file, "r") as f:
            data = json.load(f)

        stores = [s for s in data if s["onlinePlatform"] == "OSP"]
        return [IcaAPIStore.parse_obj(item) for item in stores]
