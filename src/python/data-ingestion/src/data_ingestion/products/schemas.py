"""Infer schemas for product from data."""
import json
from typing import Any, Dict

from genson import SchemaBuilder


def infer_schema(data) -> Dict[str, Any]:
    """Infer schema from data."""
    builder = SchemaBuilder()
    if not isinstance(data, list):
        data = [data]

    for item in data:
        builder.add_object(item)

    return builder.to_schema()


def infer_category_products_schema(json_file: str, output_file: str):
    """Infer schema for products by category, applicable for Coop and Axfood
    products."""
    with open(json_file, "r") as f:
        data = json.load(f)

    schema = infer_schema(data)

    with open(output_file, "w") as f:
        json.dump(schema, f, indent=2)
