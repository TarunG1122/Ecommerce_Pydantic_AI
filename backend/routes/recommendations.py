"""Personalized catalog recommendations based on a guest's in-store activity."""

from collections import Counter
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.database import interactions_collection, products_collection


router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


class Interaction(BaseModel):
    user_email: str
    action: str = Field(pattern="^(view|cart|purchase)$")
    product_name: str
    category: str = ""
    price: int = 0


def public_product(product: dict[str, Any]) -> dict[str, Any]:
    result = dict(product)
    result["id"] = str(result.pop("_id"))
    result.pop("image_data", None)
    result.pop("image_content_type", None)
    return result


def rank_products(user_email: str, limit: int = 8) -> list[dict[str, Any]]:
    interactions = list(interactions_collection.find({"user_email": user_email}))
    products = [public_product(product) for product in products_collection.find({})]
    if not products:
        return []

    weights = {"view": 1, "cart": 3, "purchase": 5}
    categories = Counter()
    prices = []
    seen_names = set()
    for interaction in interactions:
        weight = weights.get(interaction.get("action"), 1)
        if interaction.get("category"):
            categories[interaction["category"].lower()] += weight
        if interaction.get("price", 0) > 0:
            prices.append(interaction["price"])
        seen_names.add(interaction.get("product_name", "").lower())

    target_price = sum(prices) / len(prices) if prices else None
    scored = []
    for product in products:
        score = 0.0
        if product.get("category", "").lower() in categories:
            score += categories[product["category"].lower()] * 10
        if target_price:
            score += max(0, 10 - abs(product.get("price", 0) - target_price) / max(target_price, 1) * 10)
        if product.get("name", "").lower() in seen_names:
            score -= 100
        scored.append((score, product))

    return [product for _, product in sorted(scored, key=lambda item: item[0], reverse=True)[:limit]]


@router.post("/interactions")
def record_interaction(interaction: Interaction):
    record = interaction.model_dump()
    record["created_at"] = datetime.now(timezone.utc).isoformat()
    interactions_collection.insert_one(record)
    return {"message": "Interaction recorded"}


@router.get("/{user_email}")
def get_recommendations(user_email: str):
    return {"products": rank_products(user_email)}
