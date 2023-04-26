"""Infer schemas for product from data"""

from genson import SchemaBuilder


def infer_schema(data):
    """Infer schema from data"""
    builder = SchemaBuilder()
    builder.add_schema({"type": "object", "properties": {}})
    builder.add_object(data)
    return builder.to_schema()


def infer_coop_products_schema(data):
    """Infer schema for coop products from data"""
    schema = infer_schema(data)