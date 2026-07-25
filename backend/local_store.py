"""Small JSON-backed MongoDB fallback used when Atlas is unavailable."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
from pathlib import Path
import re
from threading import Lock
from typing import Any
from uuid import uuid4


DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "local_store.json"

DEMO_PRODUCTS = [
    {
        "name": "Classic Navy Oxford Shirt",
        "description": "A crisp cotton shirt for smart everyday style.",
        "price": 1499,
        "category": "men",
        "size": ["M", "L", "XL"],
        "color": ["Navy Blue"],
        "inStock": True,
        "rating": 4.6,
        "reviews": 124,
    },
    {
        "name": "Relaxed Black Hoodie",
        "description": "Soft fleece comfort with a modern relaxed fit.",
        "price": 1899,
        "category": "men",
        "size": ["S", "M", "L", "XL"],
        "color": ["Black"],
        "inStock": True,
        "rating": 4.7,
        "reviews": 87,
    },
    {
        "name": "Elegant Floral Kurti",
        "description": "Lightweight printed kurti for effortless everyday elegance.",
        "price": 1299,
        "category": "women",
        "size": ["S", "M", "L"],
        "color": ["Pink"],
        "inStock": True,
        "rating": 4.8,
        "reviews": 163,
    },
    {
        "name": "Classic Evening Dress",
        "description": "A versatile dress with a flattering, comfortable silhouette.",
        "price": 2499,
        "category": "women",
        "size": ["S", "M", "L"],
        "color": ["Burgundy"],
        "inStock": True,
        "rating": 4.5,
        "reviews": 96,
    },
    {
        "name": "Kids Adventure T-Shirt",
        "description": "Breathable cotton T-shirt made for busy play days.",
        "price": 599,
        "category": "kids",
        "size": ["S", "M", "L"],
        "color": ["Teal"],
        "inStock": True,
        "rating": 4.6,
        "reviews": 51,
    },
    {
        "name": "Kids Cozy Winter Jacket",
        "description": "Warm, lightweight jacket for cooler days.",
        "price": 2199,
        "category": "kids",
        "size": ["S", "M", "L"],
        "color": ["Red"],
        "inStock": True,
        "rating": 4.7,
        "reviews": 72,
    },
]


@dataclass
class WriteResult:
    deleted_count: int = 0
    matched_count: int = 0


class LocalCursor(list):
    def limit(self, count: int) -> "LocalCursor":
        return LocalCursor(self[:count])


class LocalStore:
    def __init__(self, path: Path = DATA_PATH):
        self.path = path
        self.lock = Lock()
        self.data = self._load()

    def _load(self) -> dict[str, list[dict[str, Any]]]:
        if self.path.exists():
            with self.path.open("r", encoding="utf-8") as file:
                return json.load(file)

        products = []
        for product in DEMO_PRODUCTS:
            item = deepcopy(product)
            item["_id"] = uuid4().hex
            products.append(item)
        return {"users": [], "products": products, "orders": [], "cart": []}

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.path.with_suffix(".tmp")
        with temporary_path.open("w", encoding="utf-8") as file:
            json.dump(self.data, file, ensure_ascii=False, indent=2)
        temporary_path.replace(self.path)


class LocalCollection:
    def __init__(self, store: LocalStore, name: str):
        self.store = store
        self.name = name

    @property
    def documents(self) -> list[dict[str, Any]]:
        return self.store.data.setdefault(self.name, [])

    def find(self, query: dict[str, Any] | None = None, projection: dict[str, int] | None = None) -> LocalCursor:
        query = query or {}
        with self.store.lock:
            matches = [deepcopy(document) for document in self.documents if _matches(document, query)]

        if projection:
            excluded = [key for key, value in projection.items() if value == 0]
            for document in matches:
                for key in excluded:
                    document.pop(key, None)
        return LocalCursor(matches)

    def count_documents(self, query: dict[str, Any]) -> int:
        return len(self.find(query))

    def insert_one(self, document: dict[str, Any]) -> WriteResult:
        self.insert_many([document])
        return WriteResult()

    def insert_many(self, documents: list[dict[str, Any]]) -> WriteResult:
        with self.store.lock:
            for document in documents:
                item = deepcopy(document)
                item.setdefault("_id", uuid4().hex)
                self.documents.append(item)
            self.store.save()
        return WriteResult()

    def delete_one(self, query: dict[str, Any]) -> WriteResult:
        with self.store.lock:
            for index, document in enumerate(self.documents):
                if _matches(document, query):
                    self.documents.pop(index)
                    self.store.save()
                    return WriteResult(deleted_count=1)
        return WriteResult()

    def delete_many(self, query: dict[str, Any]) -> WriteResult:
        with self.store.lock:
            before = len(self.documents)
            self.store.data[self.name] = [document for document in self.documents if not _matches(document, query)]
            deleted = before - len(self.store.data[self.name])
            if deleted:
                self.store.save()
        return WriteResult(deleted_count=deleted)

    def update_one(self, query: dict[str, Any], update: dict[str, dict[str, Any]]) -> WriteResult:
        with self.store.lock:
            for document in self.documents:
                if _matches(document, query):
                    document.update(deepcopy(update.get("$set", {})))
                    self.store.save()
                    return WriteResult(matched_count=1)
        return WriteResult()


def _matches(document: dict[str, Any], query: dict[str, Any]) -> bool:
    for key, expected in query.items():
        actual = document.get(key)
        if isinstance(expected, dict):
            if "$regex" in expected:
                if not isinstance(actual, str) or not re.search(expected["$regex"], actual, re.IGNORECASE if expected.get("$options") == "i" else 0):
                    return False
            else:
                if "$gte" in expected and (actual is None or actual < expected["$gte"]):
                    return False
                if "$lte" in expected and (actual is None or actual > expected["$lte"]):
                    return False
        elif str(actual) != str(expected):
            return False
    return True
