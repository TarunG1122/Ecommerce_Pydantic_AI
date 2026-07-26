"""Curated, brand-neutral apparel catalog data for the demo store."""

from __future__ import annotations

from random import Random
from typing import Any


COLORS = [
    "White", "Black", "Navy Blue", "Red", "Olive", "Beige", "Burgundy",
    "Mustard", "Grey", "Pink", "Teal", "Brown", "Blue", "Green",
]

IMAGES = {
    "men": [
        "https://images.unsplash.com/photo-1521572163474-6864f9cf17ab?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1618354691373-d851c5c3a990?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1506629905607-d405b7a8d2d4?auto=format&fit=crop&w=800&q=80",
    ],
    "women": [
        "https://images.unsplash.com/photo-1539109136881-3be0616acf4b?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1485968579580-b6d095142e6e?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1496747611176-843222e1e57c?auto=format&fit=crop&w=800&q=80",
    ],
    "kids": [
        "https://images.unsplash.com/photo-1519238263530-99bdd11df2ea?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1503919545889-aef636e10ad4?auto=format&fit=crop&w=800&q=80",
        "https://images.unsplash.com/photo-1607453998774-d533f65dac99?auto=format&fit=crop&w=800&q=80",
    ],
}

CATALOG_PROFILES = {
    "men": [
        ("T-Shirt", "cotton", "regular", "casual", "solid", 499, 1099, ["S", "M", "L", "XL", "XXL"]),
        ("Polo T-Shirt", "cotton pique", "regular", "casual", "solid", 799, 1599, ["S", "M", "L", "XL", "XXL"]),
        ("Oxford Shirt", "cotton", "slim", "smart casual", "solid", 999, 1999, ["S", "M", "L", "XL"]),
        ("Linen Shirt", "linen blend", "regular", "vacation", "solid", 1299, 2499, ["S", "M", "L", "XL"]),
        ("Checked Shirt", "cotton", "regular", "casual", "checked", 899, 1799, ["S", "M", "L", "XL"]),
        ("Slim Fit Jeans", "stretch denim", "slim", "casual", "solid", 1399, 2699, ["30", "32", "34", "36", "38"]),
        ("Tapered Chinos", "cotton twill", "tapered", "smart casual", "solid", 1299, 2499, ["30", "32", "34", "36", "38"]),
        ("Zip Hoodie", "fleece", "relaxed", "casual", "solid", 1499, 2899, ["S", "M", "L", "XL"]),
        ("Bomber Jacket", "polyester", "regular", "party", "solid", 1999, 3999, ["S", "M", "L", "XL"]),
        ("Tailored Blazer", "poly viscose", "slim", "formal", "solid", 2999, 6999, ["S", "M", "L", "XL"]),
    ],
    "women": [
        ("A-Line Midi Dress", "viscose", "regular", "casual", "floral", 1199, 2599, ["XS", "S", "M", "L", "XL"]),
        ("Fit and Flare Dress", "crepe", "regular", "party", "solid", 1499, 3299, ["XS", "S", "M", "L", "XL"]),
        ("Straight Kurti", "cotton", "regular", "ethnic", "printed", 799, 1799, ["S", "M", "L", "XL", "XXL"]),
        ("Anarkali Kurti", "rayon", "flared", "ethnic", "printed", 1199, 2799, ["S", "M", "L", "XL", "XXL"]),
        ("Co-ord Set", "cotton blend", "relaxed", "casual", "solid", 1799, 3599, ["S", "M", "L", "XL"]),
        ("High Rise Jeans", "stretch denim", "slim", "casual", "solid", 1399, 2799, ["26", "28", "30", "32", "34"]),
        ("Palazzo Pants", "viscose", "relaxed", "ethnic", "solid", 899, 1799, ["S", "M", "L", "XL"]),
        ("Satin Party Top", "satin", "regular", "party", "solid", 899, 1999, ["XS", "S", "M", "L", "XL"]),
        ("Pleated Skirt", "polyester", "flared", "casual", "solid", 999, 2199, ["XS", "S", "M", "L", "XL"]),
        ("Printed Saree", "georgette", "regular", "ethnic", "printed", 1699, 4999, ["Free Size"]),
    ],
    "kids": [
        ("Graphic T-Shirt", "cotton", "regular", "play", "graphic", 399, 899, ["2-3Y", "4-5Y", "6-7Y", "8-9Y", "10-11Y"]),
        ("Cotton Frock", "cotton", "flared", "party", "floral", 699, 1499, ["2-3Y", "4-5Y", "6-7Y", "8-9Y"]),
        ("Dungaree Set", "denim", "regular", "play", "solid", 999, 1999, ["2-3Y", "4-5Y", "6-7Y", "8-9Y"]),
        ("Track Suit", "cotton blend", "regular", "sports", "colorblock", 1099, 2299, ["4-5Y", "6-7Y", "8-9Y", "10-11Y"]),
        ("Hoodie", "fleece", "relaxed", "casual", "solid", 899, 1799, ["4-5Y", "6-7Y", "8-9Y", "10-11Y"]),
        ("Puffer Jacket", "polyester", "regular", "winter", "solid", 1499, 2999, ["4-5Y", "6-7Y", "8-9Y", "10-11Y"]),
        ("Cotton Shirt", "cotton", "regular", "party", "checked", 649, 1399, ["2-3Y", "4-5Y", "6-7Y", "8-9Y"]),
        ("Shorts Set", "cotton", "relaxed", "play", "printed", 599, 1299, ["2-3Y", "4-5Y", "6-7Y", "8-9Y"]),
        ("Festive Kurta Set", "cotton silk", "regular", "ethnic", "solid", 1199, 2599, ["2-3Y", "4-5Y", "6-7Y", "8-9Y"]),
        ("Romper", "cotton", "regular", "play", "printed", 499, 1099, ["0-3M", "3-6M", "6-9M", "9-12M"]),
    ],
}


def build_realistic_catalog(count: int = 500) -> list[dict[str, Any]]:
    """Create deterministic, varied apparel records suitable for search demos."""
    random = Random(2026)
    products: list[dict[str, Any]] = []
    categories = tuple(CATALOG_PROFILES)

    for index in range(count):
        category = categories[index % len(categories)]
        profiles = CATALOG_PROFILES[category]
        item, fabric, fit, occasion, pattern, low, high, sizes = profiles[(index // len(categories)) % len(profiles)]
        color = COLORS[(index * 5 + len(item)) % len(COLORS)]
        price = random.randrange(low, high + 1, 50)
        product_number = index + 1
        style = "minimal" if pattern in {"solid", "colorblock"} else "statement"
        image = IMAGES[category][(index // len(categories)) % len(IMAGES[category])]
        products.append({
            "name": f"ClothStore Select {color} {fabric.title()} {item}",
            "description": (
                f"{color} {item.lower()} in {fabric} with a {fit} fit and {pattern} finish. "
                f"Made for {occasion} wear with comfortable everyday styling."
            ),
            "price": price,
            "category": category,
            "size": sizes,
            "color": [color],
            "fabric": fabric,
            "fit": fit,
            "occasion": occasion,
            "pattern": pattern,
            "style": style,
            "sku": f"CS-{category[:1].upper()}-{product_number:04d}",
            "brand": "ClothStore Select",
            "image": image,
            "inStock": random.random() > 0.06,
            "rating": round(random.uniform(3.9, 4.9), 1),
            "reviews": random.randint(18, 540),
            "catalog_source": "curated_demo",
        })
    return products
