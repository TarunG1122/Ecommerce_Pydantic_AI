"""
Database configuration and MongoDB connection setup.
"""
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
import certifi
import os   
from .local_store import LocalCollection, LocalStore

# Load environment variables from .env file at root
load_dotenv(dotenv_path=os.path.join(os.getcwd(), ".env"))

# Get MongoDB connection string from environment.  The project .env uses
# MONGODB_URI; MONGO_URI remains supported for backwards compatibility.
MONGO_URI = os.getenv("MONGODB_URI") or os.getenv("MONGO_URI")

USING_LOCAL_STORE = False

try:
    if not MONGO_URI:
        raise RuntimeError("MongoDB URI is not configured")

    # Atlas requires TLS; certifi avoids Windows/OpenSSL certificate-store issues.
    client = MongoClient(
        MONGO_URI,
        tls=True,
        tlsCAFile=certifi.where(),
        serverSelectionTimeoutMS=5_000,
    )
    client.admin.command("ping")
    db = client["ecommerce_db"]
    users_collection = db["users"]
    products_collection = db["products"]
    orders_collection = db["orders"]
    cart_collection = db["cart"]
    interactions_collection = db["interactions"]
    try:
        # Supports the category/price filters and product-name search used by the app.
        products_collection.create_index([("category", 1), ("price", 1)])
        products_collection.create_index([("name", "text")])
    except PyMongoError as index_error:
        print(f"MongoDB indexes were not created: {index_error}")
except (PyMongoError, RuntimeError) as error:
    print(f"MongoDB unavailable; using local store instead: {error}")
    USING_LOCAL_STORE = True
    client = None
    db = None
    local_store = LocalStore()
    users_collection = LocalCollection(local_store, "users")
    products_collection = LocalCollection(local_store, "products")
    orders_collection = LocalCollection(local_store, "orders")
    cart_collection = LocalCollection(local_store, "cart")
    interactions_collection = LocalCollection(local_store, "interactions")


