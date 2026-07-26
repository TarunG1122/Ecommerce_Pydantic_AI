"""
Product management routes including addition, retrieval, updating, and deletion.
"""
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from ..models import Product
from ..database import products_collection
from ..catalog_seed import build_realistic_catalog
import base64
from bson import ObjectId
from typing import Optional

router = APIRouter(prefix="/products", tags=["Products"])


def product_id_query(product_id: str):
    """Support MongoDB ObjectIds and local-store string IDs."""
    try:
        return {"_id": ObjectId(product_id)}
    except Exception:
        return {"_id": product_id}

@router.post("")
async def add_product(
    name: str = Form(...),
    description: str = Form(...),
    price: int = Form(...),
    category: str = Form(...),
    size: str = Form("M,L"),
    color: str = Form("Black"),
    image: UploadFile = File(...),
):
    """
    Add a new product to the store with an image upload.
    The image is stored as base64 string in MongoDB.
    """
    # Read image file and convert to Base64
    image_data = await image.read()
    base64_image = base64.b64encode(image_data).decode("utf-8")

    # Determine content type
    content_type = image.content_type or "image/jpeg"

    # Create product document and insert into database
    product = {
        "name": name,
        "description": description,
        "price": price,
        "category": category,
        "size": size.split(","),
        "color": color.split(","),
        "image_data": base64_image,
        "image_content_type": content_type,
    }
    products_collection.insert_one(product)
    return {"message": "Product added successfully"}


@router.get("")
def get_products(
    category: str = "",
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
):
    """
    Get products with optional category, min_price, and max_price filters.
    """
    products = []
    query = {"category": {"$regex": f"^{category}$", "$options": "i"}} if category else {}

    # Apply price range filter
    if min_price is not None or max_price is not None:
        price_query = {}
        if min_price is not None:
            price_query["$gte"] = min_price
        if max_price is not None:
            price_query["$lte"] = max_price
        query["price"] = price_query

    for product in products_collection.find(query):
        product["id"] = str(product["_id"])
        product.pop("_id", None)

        # Add default fields for frontend compatibility
        if "inStock" not in product:
            product["inStock"] = True
        if "rating" not in product:
            product["rating"] = 4.5
        if "reviews" not in product:
            product["reviews"] = 0

        # If the product already has a plain image URL, use it directly
        if "image" in product and product["image"] and not isinstance(product["image"], str) is False:
            if product["image"].startswith("http"):
                pass  # Already a valid URL, keep it as-is
            elif "image_data" in product and "image_content_type" in product:
                # Convert base64 image to data URL for frontend display
                product["image"] = (
                    f"data:{product['image_content_type']};base64,{product['image_data']}"
                )
        elif "image_data" in product and "image_content_type" in product:
            # Convert base64 image to data URL for frontend display
            product["image"] = (
                f"data:{product['image_content_type']};base64,{product['image_data']}"
            )

        # Always clean up raw binary fields from response
        product.pop("image_data", None)
        product.pop("image_content_type", None)

        products.append(product)
    return products


@router.delete("")
def delete_all_products():
    """
    Delete all products from the store.
    """
    result = products_collection.delete_many({})
    return {"message": f"{result.deleted_count} products deleted"}


@router.post("/bulk-generate-500")
def bulk_generate_500(replace_existing: bool = False):
    """
    Generate a curated 500-product apparel catalog with realistic ecommerce metadata.
    Set replace_existing=true to refresh the current catalog after confirmation.
    """
    if replace_existing:
        products_collection.delete_many({})
    products_collection.insert_many(build_realistic_catalog())
    return {
        "message": "500 realistic catalog products generated successfully!",
        "replaced_existing": replace_existing,
    }

    import random

    adjectives = ["Classic", "Modern", "Premium", "Casual", "Elegant", "Trendy",
                  "Vintage", "Sporty", "Bold", "Slim", "Relaxed", "Formal"]
    colors = ["Black", "White", "Navy Blue", "Red", "Olive", "Beige",
              "Burgundy", "Mustard", "Grey", "Pink", "Teal", "Brown"]

    categories = [
        {
            "name": "men",
            "items": ["Shirt", "T-Shirt", "Jeans", "Chinos", "Blazer",
                      "Jacket", "Polo", "Sweater", "Hoodie", "Shorts"],
            "keywords": ["menswear", "mens+shirt", "mens+fashion", "mens+jacket"],
        },
        {
            "name": "women",
            "items": ["Dress", "Kurti", "Saree", "Lehenga", "Blouse",
                      "Top", "Skirt", "Palazzo", "Jumpsuit", "Cardigan"],
            "keywords": ["womens+fashion", "dress", "womens+clothing", "blouse"],
        },
        {
            "name": "kids",
            "items": ["T-Shirt", "Frock", "Dungaree", "Shorts", "Jacket",
                      "Pajama", "Romper", "Hoodie", "Sweater", "Shirt"],
            "keywords": ["kids+fashion", "children+clothing", "kids+wear"],
        },
    ]

    descriptions = [
        "A comfortable fit for everyday wear.",
        "Premium quality fabric, perfect for all occasions.",
        "Stylish and versatile — a must-have for your wardrobe.",
        "Crafted with care for maximum comfort and durability.",
        "Trendy design that keeps you looking sharp all day.",
        "Soft, breathable material ideal for the season.",
        "A timeless piece that pairs well with everything.",
        "Lightweight and easy to wear — perfect for daily use.",
        "A bold look that makes a statement.",
        "Expertly tailored for a modern silhouette.",
    ]

    sizes_pool = ["S", "M", "L", "XL", "XXL"]
    products = []

    for i in range(500):
        cat = categories[i % 3]          # cycle evenly: men, women, kids
        item = cat["items"][i % len(cat["items"])]   # cycle through item types
        adj  = adjectives[i % len(adjectives)]
        color = colors[i % len(colors)]
        keyword = cat["keywords"][i % len(cat["keywords"])]
        seed = 1000 + i

        products.append({
            "name": f"{adj} {color} {item}",
            "description": descriptions[i % len(descriptions)],
            "price": random.randint(299, 7999),
            "category": cat["name"],
            "size": random.sample(sizes_pool, k=random.randint(2, 4)),
            "color": [color],
            "image": f"https://loremflickr.com/400/500/{keyword}?lock={seed}",
            "inStock": True,
            "rating": round(random.uniform(3.5, 5.0), 1),
            "reviews": random.randint(5, 300),
        })

    products_collection.insert_many(products)
    return {"message": "500 demo products generated successfully!"}


@router.post("/bulk")
def add_multiple_products(products_list: list[Product]):
    """
    Add multiple products at once via bulk operation.
    """
    product_list = [product.model_dump() if hasattr(product, "model_dump") else product.dict() for product in products_list]
    products_collection.insert_many(product_list)
    return {"message": "Multiple products added successfully"}



@router.delete("/{id}")
def delete_product(id: str):
    """
    Delete a specific product by its ID.
    """
    result = products_collection.delete_one(product_id_query(id))

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Deleted successfully"}


@router.put("/{id}")
async def update_product(
    id: str,
    name: str = Form(None),
    description: str = Form(None),
    price: int = Form(None),
    category: str = Form(None),
    size: str = Form(None),
    color: str = Form(None),
    image: UploadFile = File(None),
):
    """
    Update an existing product's fields. Only fields provided will be modified.
    """
    # Build update dictionary with provided fields
    update_data = {}
    if name is not None:
        update_data["name"] = name
    if description is not None:
        update_data["description"] = description
    if price is not None:
        update_data["price"] = price
    if category is not None:
        update_data["category"] = category
    if size is not None:
        update_data["size"] = size.split(",")
    if color is not None:
        update_data["color"] = color.split(",")

    # Handle optional image upload
    if image:
        image_data = await image.read()
        base64_image = base64.b64encode(image_data).decode("utf-8")
        content_type = image.content_type or "image/jpeg"
        update_data["image_data"] = base64_image
        update_data["image_content_type"] = content_type

    result = products_collection.update_one(
        product_id_query(id), {"$set": update_data}
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")

    return {"message": "Product updated successfully"}
