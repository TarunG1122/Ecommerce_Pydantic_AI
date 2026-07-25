"""Vision-assisted product search for uploaded outfit images."""

import base64
import json
import os
from typing import Any

from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from openai import AsyncOpenAI

from backend.routes.chabot import OPENAI_MODEL, search_catalog


router = APIRouter(prefix="/visual-search", tags=["Visual Search"])
MAX_IMAGE_BYTES = 5 * 1024 * 1024


def clean_catalog_text(value: Any) -> str:
    """Keep simple text values without using regular expressions."""
    return "".join(char for char in str(value) if char.isalpha() or char in " -").strip().casefold()


def rank_similar(products: list[dict[str, Any]], analysis: dict[str, Any]) -> list[dict[str, Any]]:
    """Put the closest visual attributes first without excluding useful alternatives."""
    color = clean_catalog_text(analysis.get("primary_color"))
    style_terms = {clean_catalog_text(analysis.get("style")), clean_catalog_text(analysis.get("pattern"))}
    style_terms.discard("")

    def score(product: dict[str, Any]) -> int:
        product_colors = product.get("color", [])
        if isinstance(product_colors, str):
            product_colors = [product_colors]
        color_score = 20 if color in {clean_catalog_text(value) for value in product_colors} else 0
        product_text = " ".join(
            str(product.get(field, "")) for field in ("name", "description", "style", "pattern")
        ).casefold()
        style_score = sum(3 for term in style_terms if term in product_text)
        return color_score + style_score

    return sorted(products, key=score, reverse=True)


def match_catalog(analysis: dict[str, Any]) -> tuple[list[dict[str, Any]], str]:
    """Prefer exact visual matches, then return ranked similar catalog products."""
    category = clean_catalog_text(analysis.get("category"))
    if category not in {"men", "women", "kids"}:
        category = None
    keyword = clean_catalog_text(analysis.get("item_type")) or None
    primary_color = clean_catalog_text(analysis.get("primary_color")) or None

    exact_products = search_catalog(category=category, keyword=keyword, color=primary_color)
    if exact_products:
        return rank_similar(exact_products, analysis), "exact"

    # Mock catalogues may not contain the image's exact colour. In that case, keep
    # the garment type and return the closest available alternatives instead of none.
    similar_products = search_catalog(category=category, keyword=keyword)
    if similar_products:
        return rank_similar(similar_products, analysis), "similar"
    return [], "none"


async def create_no_match_reply(
    client: AsyncOpenAI,
    analysis: dict[str, Any],
    requirements: str,
) -> str:
    """Let OpenAI turn a no-match result into a helpful next question."""
    detected = {
        "category": analysis.get("category"),
        "item_type": analysis.get("item_type"),
        "primary_color": analysis.get("primary_color"),
        "style": analysis.get("style"),
        "pattern": analysis.get("pattern"),
    }
    try:
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            max_tokens=90,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a warm clothing-shopping assistant. The catalog has no genuinely similar item. "
                        "Write a concise, natural reply: acknowledge what you could not find, never invent a "
                        "product, then ask one useful follow-up question about colour, garment type, style, or budget."
                    ),
                },
                {
                    "role": "user",
                    "content": f"Detected outfit: {json.dumps(detected)}. Customer requirements: {requirements or 'none'}.",
                },
            ],
        )
        return (response.choices[0].message.content or "").strip()
    except Exception:
        item = analysis.get("item_type") or "item"
        return f"I could not find a similar {item} in the catalog. Would you like to change the colour, style, or budget?"


@router.post("")
async def visual_search(image: UploadFile = File(...), requirements: str = Form("")):
    if image.content_type not in {"image/jpeg", "image/jpg", "image/png", "image/webp"}:
        raise HTTPException(status_code=415, detail="Upload a JPG, PNG, or WebP outfit image.")

    image_bytes = await image.read()
    if not image_bytes or len(image_bytes) > MAX_IMAGE_BYTES:
        raise HTTPException(status_code=400, detail="Image must be between 1 byte and 5 MB.")
    if not os.getenv("OPENAI_API_KEY"):
        raise HTTPException(status_code=503, detail="Visual search is not configured.")

    data_url = f"data:{image.content_type};base64,{base64.b64encode(image_bytes).decode('ascii')}"
    requirements = requirements.strip()[:300]
    client = AsyncOpenAI()
    try:
        response = await client.chat.completions.create(
            model=OPENAI_MODEL,
            response_format={"type": "json_object"},
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict clothing-catalog query extractor. Return JSON only with category "
                        "(men, women, kids, or null), item_type, primary_color, style, and pattern. Identify the "
                        "dominant garment. Customer requirements are important and override uncertain visual "
                        "details. primary_color must be one simple colour name or null when uncertain. Pattern "
                        "should be one of plain, solid, striped, printed, graphic, textured, or null."
                    ),
                },
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": f"Analyze this outfit for a strict catalog search. Customer requirements: {requirements or 'none'}",
                        },
                        {"type": "image_url", "image_url": {"url": data_url, "detail": "low"}},
                    ],
                },
            ],
        )
        analysis = json.loads(response.choices[0].message.content or "{}")
    except Exception as error:
        raise HTTPException(status_code=502, detail="Could not analyze the outfit image.") from error

    analysis["item_type"] = clean_catalog_text(analysis.get("item_type"))
    analysis["primary_color"] = clean_catalog_text(analysis.get("primary_color")) or None
    analysis["style"] = clean_catalog_text(analysis.get("style")) or None
    analysis["pattern"] = clean_catalog_text(analysis.get("pattern")) or None
    products, match_type = match_catalog(analysis)
    assistant_message = None
    if match_type == "none":
        assistant_message = await create_no_match_reply(client, analysis, requirements)
    return {
        "analysis": analysis,
        "products": products,
        "match_type": match_type,
        "assistant_message": assistant_message,
    }
