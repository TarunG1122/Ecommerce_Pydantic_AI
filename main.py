from fastapi import FastAPI

from backend.routes import products, orders, cart, chatbot, recommendations, visual_search
from backend.chatbot_evals import run_chatbot_evaluations
from backend.database import (
    USING_LOCAL_STORE,
    cart_collection,
    orders_collection,
    products_collection,
)
import os
import uvicorn
import logfire

# Initialize FastAPI app
app = FastAPI()


# Configure Logfire for Observability
logfire.configure(send_to_logfire='if-token-present')
logfire.instrument_fastapi(app)
logfire.instrument_pydantic()

# Create uploads folder for product images
UPLOAD_FOLDER = "uploads"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    

# Include API route modules
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(cart.router)
app.include_router(chatbot.router)
app.include_router(recommendations.router)
app.include_router(visual_search.router)

# Catch fast-search regressions at application startup without calling OpenAI.
chatbot_evaluation_failures = run_chatbot_evaluations()
if chatbot_evaluation_failures:
    raise RuntimeError(f"Chatbot evaluation failures: {chatbot_evaluation_failures}")
print("Chatbot evaluations passed.")


@app.get("/health")
def health_check():
    """Report whether the application is using Atlas or the local fallback."""
    return {
        "status": "ok",
        "storage": "local fallback" if USING_LOCAL_STORE else "mongodb",
    }


@app.get("/admin/metrics")
def admin_metrics():
    """Small operational summary for the Admin dashboard."""
    return {
        "storage": "local fallback" if USING_LOCAL_STORE else "mongodb",
        "products": products_collection.count_documents({}),
        "orders": orders_collection.count_documents({}),
        "cart_items": cart_collection.count_documents({}),
    }

# Serve uploaded files statically
from fastapi.staticfiles import StaticFiles
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Serve Frontend natively
app.mount("/", StaticFiles(directory="Frontend", html=True), name="frontend")

if __name__ == "__main__":
    print("⚙️ Starting backend server (FastAPI)...")
    port = int(os.getenv("PORT", "8000"))
    print(f"Starting backend server (FastAPI) on port {port}...")
    print(f"Open http://127.0.0.1:{port}/ in your browser.")
    uvicorn.run(app, host="0.0.0.0", port=port)
