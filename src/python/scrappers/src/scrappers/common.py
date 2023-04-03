"""Common utilities for data aggregators."""
import itertools
import json
import math
import os
import random
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from urllib.parse import urlencode, urljoin

from loguru import logger

USER_AGENTS = [
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/109.0",
    (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36 "
        "Edg/110.0.1587.41"
    ),
    (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 "
        "Safari/537.36"
    ),
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/109.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/110.0",
]


def get_file_list(dir: Any, file_ext: str):
    """Returns a list of files from the directory that has extension specified
    by `file_ext`"""
    file_list = [f for f in os.listdir(dir) if f.endswith(file_ext)]
    return [os.path.join(dir, f) for f in file_list]


def random_user_agents() -> str:
    return random.choice(USER_AGENTS)


def init_storage_dir(
    parent_path: Any,
    dirname: str,
    create_daily_dir: bool = True,
    sub_dir: Optional[str] = None,
) -> Path:
    """Create directory to store the scrapped data if neccessary.

    Args:
        create_daily_dir: If True, create a sub-directory of current date under dirname,
            where the data will be stored
    """
    path = parent_path / dirname
    if create_daily_dir:
        date = datetime.utcnow().strftime("%Y%m%d")
        path = path / date

    if sub_dir is not None:
        path = path / sub_dir

    if not os.path.exists(path):
        os.makedirs(path, exist_ok=True)

    return path


def write_category_data(category: str, data: Any, data_path: Any) -> None:
    """Write product's information of a category into JSON file. The file
    format is `[category-slug]_[timestamp].json`

    Args:
        category: name of the category (in slug format)
        data: often list of products information
        data_path: directory to write the JSON file to
    """
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")

    file_name = f"{category}_{timestamp}.json"
    file_path = os.path.join(data_path, file_name)

    logger.info(f"Writing {len(data)} result(s) to {file_path}")
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)


def partition_data(
    data: Union[List, Dict[str, str]],
    num_partitions: Optional[int] = None,
    partitions_size: Optional[int] = None,
) -> List[Any]:
    """Partition the data into chunks of equal size (as good as possible)

    Args:
        data: iterable object to be partitioned
        num_partitions: Number of partitions that the data list is divided into
        partitions_size: Size of each partition. Either `num_partitions` or `partition_size` should be set, not both.

    Returns:
        If `data` is a list, return a list containing partitions.
        If `data` is a dictionary, return a list containing partition whose elements are
        values from the original dictionary.
    """
    if not isinstance(data, (list, dict)):
        raise ValueError("Data must either be a list or a dictionary")

    if num_partitions and partitions_size:
        raise ValueError(
            "Either `num_partitions` or `partition_size` should be set, not both."
        )

    if isinstance(data, dict):
        data = data.values()

    if num_partitions:
        p_size = math.ceil(len(data) / num_partitions)
    else:
        p_size = partitions_size

    def partition(lst, size):
        for i in range(0, len(lst), size):
            yield list(itertools.islice(lst, i, i + size))

    return list(partition(data, p_size))


def make_url(base_url: str, params: Dict[str, Any]) -> str:
    """Encode search params and make a full url."""
    qs = urlencode(params)
    return urljoin(base_url, "?" + qs)
