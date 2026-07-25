"""
Pydantic models for data validation and serialization.
"""    

from pydantic import BaseModel
from typing import Optional, List

## type hiniting

class Product(BaseModel):
    """Product model for the store inventory."""
    name: str
    description: str
    price: int
    category: str
    size: List[str]  #m , # s # L # xl
    color: List[str] # red, blue, green, yellow, black, white, purple, pink, orange, brown, gray, etc.
    image: str  # url of picsum photos 


class Order(BaseModel):
    """Order placement model."""
    user_email: str
    product_name: str
    quantity: int


class CartItem(BaseModel):
    """Shopping cart item model."""
    user_email: str
    product_name: str
    quantity: int
