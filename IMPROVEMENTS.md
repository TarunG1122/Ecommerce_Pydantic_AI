# Interview-ready improvements

## What has been added

### 1. Fast hybrid chatbot search

OpenAI interprets every shopping request, including short prompts such as `show women dress under 3000` and `white shirt`, and calls the catalog-search tool with structured filters.

- This avoids unnecessary follow-up questions while allowing natural-language understanding.
- Product searches use OpenAI `gpt-4o-mini` through the chatbot tool call.
- A colour request is an exact match against the product's stored `color` value, so `white shirt` never returns a black shirt. If no white shirt exists, it reports no result instead of substituting another colour.
- Greetings and open-ended shopping conversations still use the OpenAI chatbot.

The implementation is in `backend/routes/chabot.py`.

### 2. Chatbot guardrail evaluation script

`scripts/evaluate_chatbot.py` tests the server-side catalog guardrails without using OpenAI credits.

These checks also run automatically whenever you start the application with `python main.py`. They verify that the filters selected by OpenAI are applied safely, including rejecting a black shirt for a `white shirt` request.

Run it from the project root:

```powershell
.\ecpyenv\Scripts\python.exe scripts\evaluate_chatbot.py
```

Add a new case whenever the chatbot misunderstands a customer query. This gives you a concrete quality-regression story for an interview.

### 3. Admin operational metrics

The Admin page now shows the active storage mode and counts for products, orders, and cart items.

The API endpoint is `GET /admin/metrics`.

- `mongodb` means Atlas is connected.
- `local fallback` means the app is preserving functionality while Atlas is unreachable.

### 4. MongoDB search indexes

When MongoDB connects, the app creates indexes for:

- `category` + `price` for filtered catalog queries.
- Text search on product `name`.

This gives a useful performance discussion point in an interview.

## Still recommended before production

1. Add login and admin-only authorization before exposing product management.
2. Add MongoDB schema validation for products and orders.
3. Track chatbot latency, zero-result searches, and conversion to cart/orders in Logfire or a dashboard.
4. Add size and occasion filters to the fast chatbot search.
5. Replace the development local-store fallback with a managed database deployment once Atlas networking is resolved.

## Visual search and personalized recommendations

### Visual search

The image uploader is embedded in the chatbot: open **Chat**, select an outfit image (JPG, PNG, or WebP, up to 5 MB), optionally type strict requirements such as `white T-shirt under Rs. 2000`, then choose **Search by image**. It sends the image and requirements to `POST /visual-search` and presents the matches as a chatbot reply.

Technology: FastAPI file upload, OpenAI `gpt-4o-mini` vision input, structured JSON attributes, and similarity ranking. The search tries an exact garment-and-colour match first. When generated mock products do not contain that exact colour, it returns similar garments ranked by colour, style, and pattern. When there is no genuinely similar garment type, OpenAI provides a short, interactive follow-up question instead of unrelated products. The app does not save the uploaded image.

Uploaded outfit images are shown in the customer message bubble. The chatbot starts empty; normal text messages, including greetings, are handled by OpenAI.

### Personalized recommendations

The storefront records product views and cart events for the current anonymous guest session. `GET /recommendations/{user_email}` ranks products based on category affinity, action strength (view/cart/purchase), and budget similarity.

Technology: FastAPI, MongoDB (or the local fallback), deterministic ranking, and browser `localStorage` for the anonymous guest ID.

## Suggested interview explanation

"I use OpenAI function calling to understand natural-language shopping requests, then apply its selected filters through strict server-side catalog guardrails. I added evaluations to prevent regressions, database indexes for scalable search, operational metrics for visibility, and a graceful storage fallback for reliability."
