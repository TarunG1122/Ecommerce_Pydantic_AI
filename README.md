# ClothStore AI - GenAI-Powered Clothing Store

ClothStore AI is an end-to-end clothing-commerce prototype that combines a curated product catalogue with an AI shopping assistant, optional visual search, personalised recommendations, MongoDB persistence, and containerised deployment.

It is designed to demonstrate more than a chatbot: the assistant understands shopping constraints, searches real catalogue fields through controlled tools, carries context across turns, and gives helpful alternatives when an exact product is unavailable.

**Live application:** [http://3.27.13.190:8000/](http://3.27.13.190:8000/)

## Why this project stands out

| Challenge | Implementation | Value |
| --- | --- | --- |
| Generic chatbot answers | OpenAI-powered assistant calls a constrained catalogue-search tool | Results come from the store's actual inventory, not invented products |
| Multi-turn shopping requests | Recent conversation history is passed with each chat request | A user can say "red dress", then "under Rs. 3000" without repeating the colour or item |
| Image-only product discovery | Optional image upload plus a text requirement in the same chat composer | Users can ask for visually similar items while still specifying budget, category, or style |
| Unreliable external services | MongoDB health check with a local JSON fallback | The storefront remains usable during database/network problems |
| Random demo products | Deterministic, realistic 500-item fashion catalogue | Better demonstrations, filtering, and recommendations |
| LLM cost and safety | `gpt-4o-mini`, low-detail image analysis, bounded history, and deterministic filtering | Practical AI behaviour without sending unnecessary context or allowing uncontrolled queries |

## Key capabilities

- **Conversational product discovery:** searches by item, category, price, colour, fabric, fit, occasion, and pattern.
- **Conversation memory:** combines previously stated requirements before searching, rather than repeatedly asking the same questions.
- **Visual search inside chat:** upload an outfit image only when needed, add optional requirements in the normal message field, and see the uploaded image in the conversation.
- **Similar-item fallback:** if an exact visual match is unavailable, the assistant explains the gap and offers the closest catalogue alternatives or a useful follow-up question.
- **Personalised recommendations:** ranks products from click/view, cart, and purchase signals, category affinity, and budget preference.
- **Admin operations:** refresh the curated 500-product catalogue and inspect product, order, cart, and storage-mode metrics.
- **Resilient data layer:** uses MongoDB when available and falls back to a local store for demos and development.
- **Production-ready delivery basics:** Docker, health checks, `.dockerignore`, GitHub Actions CI/CD, and environment-based secrets.

## Key highlights

- The AI assistant is grounded in the application's own product catalogue, so it returns inventory-backed results rather than fictional recommendations.
- Users can combine image search and natural-language requirements in one chat message, for example: "Find T-shirts like this under Rs. 5000."
- Conversation context is retained across recent messages, enabling natural refinement of a search without repeatedly entering the same requirements.
- The 500-product curated catalogue contains rich metadata that supports accurate filters and meaningful visual similarity ranking.
- MongoDB provides production persistence, while the local JSON fallback prevents a database outage from making the application unusable.
- The application is containerised and deployed on AWS using Amazon ECR, an EC2 instance, and GitHub Actions.

## Architecture

```text
Browser (vanilla JavaScript)
        |
        | REST + multipart image upload
        v
FastAPI application (main.py)
        |
        +--> Product / Cart / Order / Admin APIs
        |
        +--> AI chat route
        |       |
        |       +--> Pydantic AI + OpenAI gpt-4o-mini
        |       |       |
        |       |       +--> Controlled catalogue-search tool
        |       |
        |       +--> Bounded conversation history
        |
        +--> Visual search route
        |       |
        |       +--> Vision attributes -> exact/similar catalogue ranking
        |
        +--> Recommendation route
                |
                v
       MongoDB Atlas  <---->  Local JSON fallback
```

The frontend is deliberately lightweight: FastAPI serves the static application directly, so local development does not require a separate Node build server.

## Technology stack

| Area | Tools and technologies | Purpose |
| --- | --- | --- |
| Frontend | HTML, CSS, modern vanilla JavaScript | Responsive storefront, cart, admin panel, and chat user interface |
| Backend | Python 3.13, FastAPI, Uvicorn, Pydantic | Typed REST API, validation, asynchronous endpoints, static-file serving |
| AI orchestration | Pydantic AI, OpenAI API, `gpt-4o-mini` | Tool-based shopping conversation and lower-cost vision/text analysis |
| Data | MongoDB Atlas, PyMongo, Certifi | Persistent product, cart, order, and interaction data with TLS support |
| Resilience | Local JSON store | Graceful development/demo fallback when MongoDB is unavailable |
| Observability | Logfire (optional) | Request and application tracing when a token is configured |
| Quality | `py_compile`, deterministic chatbot evaluations | Syntax checks and regression checks that do not consume OpenAI credits |
| Delivery | Docker, Docker Compose-compatible image, GitHub Actions, AWS ECR/EC2 self-hosted runner | Repeatable container builds and deployment automation |

## How the AI assistant works

### 1. Normal text shopping chat

1. The user sends a message such as: `I need a red dress`.
2. The frontend sends that message plus a short, bounded chat history to `POST /chat`.
3. The OpenAI model interprets the intent and calls the application's `search_products` tool with structured fields.
4. The tool filters only the local catalogue data: item/category, price range, colour, fabric, fit, occasion, and pattern.
5. The model presents the returned products conversationally. It asks a follow-up question only if a missing detail is genuinely needed.

For example, after `I need a red dress`, the follow-up `under Rs. 3000` is understood as **red dress + maximum price Rs. 3000**, not as a new unrelated search.

### 2. Why tool calling matters

The language model is responsible for understanding natural language and maintaining a helpful conversation. It is **not** trusted to invent inventory. Product retrieval happens through a controlled Python tool with explicit filters, so every displayed result is backed by the catalogue.

This separation uses the LLM where it is strongest at language, while deterministic code enforces accuracy and business rules.

### 3. Visual search in the same chat experience

1. The user optionally chooses an image using **Attach image** and can type requirements in the existing chat field, for example: `T-shirts under Rs. 5000 in the same colour`.
2. The frontend previews the image in the user's chat bubble and posts it to `POST /visual-search`.
3. A low-detail vision request extracts clothing attributes such as garment type, primary colour, style, and pattern.
4. Backend code first looks for the closest attribute match, then ranks similar products by item type, colour, style, and pattern.
5. If the catalogue has no meaningful match, the assistant gives an honest, interactive answer instead of falsely claiming an exact match.

Uploaded images are used for the search request and preview; they are not saved as customer profile photos by the application.

### 4. Personalised recommendations

The application records product interactions as `view`, `cart`, or `purchase`. Recommendation ranking gives stronger weight to cart and purchase events, then uses category affinity and a user's observed price range to rank unseen products. This is intentionally explainable and can later be upgraded to embeddings or collaborative filtering without changing the user experience.

## Data and catalogue design

The seeded catalogue contains **500 deterministic fashion products** across men's, women's, and kids' categories. Each product includes useful search metadata:

- name and description
- price and category
- colour, size, fabric, fit, occasion, pattern, and style
- SKU, brand, stock, rating, and review count
- stable product image URL

Use the Admin page's **Refresh 500 Realistic Products** action to replace demo products with this catalogue. It intentionally replaces existing products, so only use it in a development/demo environment.

MongoDB is the preferred storage mode. At startup, the backend performs a short database health check and creates helpful product indexes when it connects. If the connection fails, it switches to `data/local_store.json` and reports that mode through the admin metrics endpoint. This keeps the project demonstrable even if Atlas IP access, DNS, TLS, or credentials are not configured correctly.

## API overview

| Endpoint | Method | Use |
| --- | --- | --- |
| `/products` | `GET` | List/filter catalogue products |
| `/products/bulk-generate-500` | `POST` | Seed or refresh the realistic catalogue |
| `/chat` | `POST` | Text shopping assistant with conversation history |
| `/visual-search` | `POST` | Image-based similar product search with optional text requirements |
| `/recommendations/{user_email}` | `GET` | Retrieve personalised product suggestions |
| `/interactions` | `POST` | Record view, cart, or purchase signals |
| `/admin/metrics` | `GET` | Inspect storage mode and operational counts |
| `/health` | `GET` | Container and load-balancer health check |

## Run locally

### Prerequisites

- Python 3.13 (the Docker image uses Python 3.13)
- An OpenAI API key for AI chat and visual search
- MongoDB Atlas is recommended, but optional because the local fallback is available

### Setup on Windows PowerShell

```powershell
Copy-Item .env.example .env
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python main.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000) in a browser. Use `127.0.0.1` or `localhost` in the browser; `0.0.0.0` is a server bind address, not a browser destination.

If PowerShell blocks activation, run this once for the current session:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Environment configuration

Create `.env` from `.env.example`; never commit the real file.

| Variable | Required | Description |
| --- | --- | --- |
| `OPENAI_API_KEY` | Yes for AI features | Enables chat and visual-search analysis |
| `MONGODB_URI` or `MONGO_URI` | Recommended | MongoDB Atlas connection string; the app falls back locally if unavailable |
| `PORT` | No | Server port; defaults to `8000` |
| `LOGFIRE_TOKEN` | No | Enables Logfire tracing when configured |
| `GROQ_API_KEY` | No | Kept for compatibility; the current chat/vision flows use OpenAI |

Do not place passwords, API keys, Atlas credentials, or certificate files in source control. The repository's `.gitignore` and `.dockerignore` exclude them.

## Run with Docker

```powershell
docker build -t clothstore-ai .
docker run --rm -p 8000:8000 --env-file .env clothstore-ai
```

Then browse to [http://127.0.0.1:8000](http://127.0.0.1:8000). The image runs as a non-root user and exposes a `/health` endpoint for Docker and deployment checks.

For a persistent local fallback catalogue during container development, mount the `data` directory as a volume appropriate for your operating system.

## Validate the project

Run the deterministic chatbot checks from the project root:

```powershell
.\ecpyenv\Scripts\python.exe scripts\evaluate_chatbot.py
```

These checks verify strict colour/budget matching and conversation-memory formatting without making OpenAI API calls. The same evaluation guard also runs during application startup, which catches a regression before the server begins accepting traffic.

Useful additional checks:

```powershell
.\ecpyenv\Scripts\python.exe -m py_compile main.py backend\routes\chabot.py backend\routes\visual_search.py
docker build -t clothstore-ai .
```

## CI/CD and AWS deployment

The live application is available at [http://3.27.13.190:8000/](http://3.27.13.190:8000/). It is deployed to an AWS EC2 instance and runs as the Docker container named `luxe-app` on port `8000`.

The deployment workflow in `.github/workflows/cicd.yaml` automates the following process:

1. A push to the configured branch starts GitHub Actions.
2. The workflow builds the Docker image from the repository's `Dockerfile`.
3. GitHub Actions authenticates with AWS and pushes the image to **Amazon Elastic Container Registry (ECR)**.
4. A self-hosted GitHub Actions runner on the EC2 instance receives the deployment job.
5. The runner pulls the latest image from ECR, replaces the previous `luxe-app` container, and maps EC2 port `8000` to container port `8000`.
6. Docker's health check requests `/health` to confirm that the container is running correctly.

This approach keeps the application image in a private container registry, makes deployments repeatable, and allows the EC2 server to update without manually copying project files.

Configure these GitHub repository secrets before deployment:

| Secret | Purpose |
| --- | --- |
| `AWS_ACCESS_KEY_ID` | AWS authentication for ECR |
| `AWS_SECRET_ACCESS_KEY` | AWS authentication for ECR |
| `AWS_DEFAULT_REGION` | AWS region for ECR |
| `ECR_REPO` | ECR repository name/URI used by the workflow |
| `OPENAI_API_KEY` | Production AI chat and visual-search access |
| `MONGO_URI` | Production MongoDB connection string |
| `LOGFIRE_TOKEN` | Optional production observability |
| `GROQ_API_KEY` | Optional compatibility secret |

On the EC2 runner, the Actions service should be enabled so deployments do not remain queued:

```bash
cd /home/ubuntu/actions-runner
sudo ./svc.sh status
```

## Project structure

```text
.
backend/
|-- routes/                     # Product, cart, order, chat, visual-search, recommendation APIs
|-- catalog_seed.py             # Deterministic 500-product fashion catalogue
|-- chatbot_evals.py            # No-credit regression checks
|-- database.py                 # MongoDB connection and fallback selection
|-- local_store.py              # JSON-backed development fallback
Frontend/                       # Static vanilla-JS storefront and chat UI
data/                           # Local fallback data
scripts/evaluate_chatbot.py     # Standalone evaluation command
.github/workflows/cicd.yaml     # Build/push/deploy workflow
Dockerfile                      # Python 3.13 production container
.dockerignore                   # Lean, safer Docker build context
.env.example                    # Safe configuration template
main.py                         # FastAPI application entry point
```

## Future enhancements

- Add authentication, role-based admin access, and per-user recommendation profiles.
- Replace external placeholder image URLs with licensed, internally hosted product media.
- Store visual embeddings in a vector database for richer similarity beyond catalogue metadata.
- Add inventory reservation, payment integration, order status workflows, and transactional consistency.
- Track retrieval quality, tool-call success, latency, and user feedback in dashboards.
- Introduce automated API, UI, and end-to-end deployment tests in CI.
- Add guardrails for abusive uploads, rate limiting, and image moderation before a public launch.

## Important notes

This is a portfolio and learning project, not a production payment system. Before handling real customers, add authentication, authorisation, compliance review, image/content moderation, monitoring, rate limits, robust test coverage, and a licensed product catalogue.

---

Built to demonstrate practical GenAI engineering: useful user experience, grounded retrieval, predictable backend logic, resilient data handling, and deployable infrastructure.
