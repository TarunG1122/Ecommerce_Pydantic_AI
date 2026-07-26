"""OpenAI-powered shopping chatbot with strict catalog guardrails."""

from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from fastapi import APIRouter, Body
from pydantic import BaseModel
from pydantic_ai import Agent, RunContext

from backend.database import products_collection


load_dotenv()

router = APIRouter(prefix="/chat", tags=["Chatbot"])
OPENAI_MODEL = "gpt-4o-mini"
MAX_HISTORY_MESSAGES = 10
MAX_HISTORY_MESSAGE_LENGTH = 500


def format_chat_history(history: Any) -> str:
    """Create a bounded, text-only memory of the preceding customer conversation."""
    if not isinstance(history, list):
        return ""

    formatted = []
    for turn in history[-MAX_HISTORY_MESSAGES:]:
        if not isinstance(turn, dict):
            continue
        role = turn.get("role")
        content = turn.get("content")
        if role not in {"user", "assistant"} or not isinstance(content, str):
            continue
        content = content.strip()[:MAX_HISTORY_MESSAGE_LENGTH]
        if content:
            speaker = "Customer" if role == "user" else "Assistant"
            formatted.append(f"{speaker}: {content}")
    return "\n".join(formatted)


def product_matches(
    product: Dict[str, Any],
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    max_price: Optional[int] = None,
    min_price: Optional[int] = None,
    color: Optional[str] = None,
    fabric: Optional[str] = None,
    fit: Optional[str] = None,
    occasion: Optional[str] = None,
    pattern: Optional[str] = None,
) -> bool:
    """Strictly apply the filters selected by OpenAI to one catalog product."""
    if category and str(product.get("category", "")).casefold() != category.strip().casefold():
        return False
    if keyword and keyword.strip().casefold() not in str(product.get("name", "")).casefold():
        return False
    if max_price is not None and product.get("price", 0) > max_price:
        return False
    if min_price is not None and product.get("price", 0) < min_price:
        return False

    product_colors = product.get("color", [])
    if isinstance(product_colors, str):
        product_colors = [product_colors]
    if color and color.strip().casefold() not in {str(value).strip().casefold() for value in product_colors}:
        return False
    for requested, field in ((fabric, "fabric"), (fit, "fit"), (occasion, "occasion"), (pattern, "pattern")):
        if requested and requested.strip().casefold() not in str(product.get(field, "")).casefold():
            return False
    return True


def search_catalog(
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    max_price: Optional[int] = None,
    min_price: Optional[int] = None,
    color: Optional[str] = None,
    fabric: Optional[str] = None,
    fit: Optional[str] = None,
    occasion: Optional[str] = None,
    pattern: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Search products using OpenAI-selected filters, without regex matching."""
    results = []
    for product in products_collection.find({}):
        if not product_matches(product, category, keyword, max_price, min_price, color, fabric, fit, occasion, pattern):
            continue
        product["id"] = str(product.pop("_id"))
        product.pop("image_data", None)
        product.pop("image_content_type", None)
        results.append(product)
        if len(results) == 8:
            break
    return results


class StoreDeps(BaseModel):
    """Holds products returned by the OpenAI tool call."""

    found_products: List[Dict[str, Any]] = []

    class Config:
        arbitrary_types_allowed = True


agent = Agent(
    f"openai:{OPENAI_MODEL}",
    deps_type=StoreDeps,
    system_prompt=(
        "You are the product-search assistant for ClothStore, an online clothing store. "
        "The store categories are men, women, and kids. "
        "For every request that names clothing, category, colour, budget, or product search intent, "
        "call search_products exactly once with all stated filters. This includes short prompts such as "
        "'white shirt'. Always put an explicitly requested colour in color exactly as requested; never "
        "substitute a similar colour. The customer may add details over multiple messages: combine all prior "
        "customer requirements with the latest message before searching. For example, a prior 'red dress' plus "
        "a latest 'under 3000' means search red dresses under 3000. Never ask for a colour, price, category, "
        "or item that the customer has already provided; search with the known information instead. Do not invent "
        "product data. Extract fabric, fit, occasion, and pattern whenever the customer mentions them, then pass "
        "them to the search tool. For greetings, reply warmly. For unrelated requests, reply that you can only help with "
        "clothing shopping."
    ),
)


@agent.tool
def search_products(
    ctx: RunContext[StoreDeps],
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    max_price: Optional[int] = None,
    min_price: Optional[int] = None,
    color: Optional[str] = None,
    fabric: Optional[str] = None,
    fit: Optional[str] = None,
    occasion: Optional[str] = None,
    pattern: Optional[str] = None,
) -> str:
    """Search products by item, price, colour, fabric, fit, occasion, and pattern."""
    products = search_catalog(category, keyword, max_price, min_price, color, fabric, fit, occasion, pattern)
    ctx.deps.found_products = products
    if not products:
        return "No products found matching those filters."
    return f"Found {len(products)} products matching the request."


@router.post("")
async def chat_bot(data: dict = Body(...)):
    """Use OpenAI to understand a request, then return its guarded catalog results."""
    user_message = data.get("message", "").strip()
    if not user_message:
        return {"type": "text", "message": "Please type a message!", "data": None}

    history_text = format_chat_history(data.get("history"))
    agent_input = user_message
    if history_text:
        agent_input = (
            "Previous conversation for context. Use it only to retain the customer's shopping requirements:\n"
            f"{history_text}\n\n"
            f"Latest customer message: {user_message}"
        )

    deps = StoreDeps()
    try:
        result = await agent.run(agent_input, deps=deps)
        if deps.found_products:
            return {"type": "products", "message": result.output, "data": deps.found_products}
        return {"type": "text", "message": result.output, "data": None}
    except Exception as error:
        print(f"[Chatbot Error] {error}")
        return {
            "type": "text",
            "message": "Sorry, I could not complete that search. Please try again.",
            "data": None,
        }
