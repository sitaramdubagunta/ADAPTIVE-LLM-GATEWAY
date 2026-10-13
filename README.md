# Adaptive LLM Gateway

An adaptive FastAPI + React application that routes chat requests across multiple LLM providers based on prompt type, capability, and fallback behavior. The project uses PostgreSQL with `pgvector` for route prototype embeddings, JWT authentication for users, and a streaming chat UI built with React and Vite.

## Live Deployment

| Component | Host | URL |
| --- | --- | --- |
| Frontend (React + Vite) | Vercel | https://frontend-green-theta-51.vercel.app |
| Backend (FastAPI, Docker) | Google Cloud Run (`us-central1`) | https://llm-gateway-446264156579.us-central1.run.app |
| Database (PostgreSQL + pgvector) | Neon | managed, connection string in `DATABASE_URL` |

Interactive API docs: https://llm-gateway-446264156579.us-central1.run.app/docs

The backend scales to zero, so the first request after a quiet period can take a few seconds while the container and embedding model start. See [Deployment](#deployment) for how it is set up.

## Screenshots

### Landing Page

![Landing page](screenshots/01-landing-page.png)

### Auth Screen

![Authentication screen](screenshots/02-auth-screen.png)

### Chat Dashboard

![Chat dashboard](screenshots/03-chat-dashboard.png)

### Streaming Response

![Streaming response](screenshots/04-streaming-response.png)

### Chat History

![Chat history](screenshots/05-chat-history.png)

## Features

- Adaptive LLM routing between Groq and Gemini providers
- Streaming chat responses with Server-Sent Events
- JWT-based login and registration flow
- PostgreSQL persistence for users, chats, requests, and responses
- `pgvector` route prototypes for embedding-based routing
- Provider fallback behavior for quota and availability errors
- React dashboard with chat history and markdown rendering
- Dockerfile for containerizing the FastAPI backend

## Tech Stack

**Frontend**

- React
- Vite
- Tailwind CSS
- React Router
- React Markdown

**Backend**

- FastAPI
- Uvicorn
- SQLAlchemy
- PostgreSQL
- pgvector
- Sentence Transformers
- Groq SDK
- Google GenAI SDK
- JWT authentication

## Project Structure

```text
llm-gateway/
+-- backend/
|   +-- database/
|   |   +-- database.py
|   |   +-- models.py
|   |   +-- schema.sql
|   |   +-- seed_prototype.py
|   |   +-- session.py
|   +-- providers/
|   +-- routes/
|   +-- services/
|   +-- Dockerfile
|   +-- main.py
|   +-- requirements.txt
+-- frontend/
|   +-- public/
|   +-- src/
|   +-- package.json
|   +-- vite.config.js
+-- screenshots/
+-- docker-compose.yml
```

## Environment Variables

Create `backend/.env` for local development:

```env
GEMINI_API_KEY=your_gemini_api_key
GROQ_API_KEY=your_groq_api_key
JWT_SECRET_KEY=replace_with_a_long_random_secret
JWT_EXPIRE_MINUTES=30
DATABASE_URL=postgresql://postgres:postgres@localhost:5433/llm_gateway
CORS_ORIGINS=http://localhost:5173,http://localhost:5174
```

`CORS_ORIGINS` is a comma-separated list of allowed frontend origins (defaults to the two localhost origins above). The frontend reads the backend address from `VITE_API_URL` and falls back to `http://localhost:8000`.

For Docker, set `DATABASE_URL` to the database container hostname on the shared Docker network, for example:

```env
DATABASE_URL=postgresql://postgres:postgres@llm_gateway_db:5432/llm_gateway
```

## Local Development

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend currently expects the backend at:

```text
http://localhost:8000
```

## Database Setup

The app expects PostgreSQL with the `pgvector` extension enabled. The schema is available at:

```text
backend/database/schema.sql
```

After creating the schema, seed route prototypes with:

```bash
cd backend
python database/seed_prototype.py
```

## Docker Backend

Build the backend image:

```bash
docker build -t llm-gateway-backend ./backend
```

Run it on the same Docker network as the existing PostgreSQL container. The container listens on `$PORT` (default `8080`), so map it to `8000` locally:

```bash
docker run --name llm_gateway_backend --rm \
  --network <db-network-name> \
  -p 8000:8080 \
  --env-file backend/.env \
  -e DATABASE_URL=postgresql://postgres:postgres@llm_gateway_db:5432/llm_gateway \
  llm-gateway-backend
```

## Deployment

The app is deployed on free tiers: Vercel (frontend), Google Cloud Run (backend) and Neon (database).

### 1. Database (Neon)

1. Create a Neon project and copy its connection string.
2. Apply `backend/database/schema.sql` (it enables `pgvector`), then seed the routes with `python backend/database/seed_prototype.py`, using the **unpooled** connection string for both.
3. Use the **pooled** connection string as `DATABASE_URL` for the running backend.

`DATABASE_URL` may be a plain `postgresql://` URL; the backend switches it to the `psycopg2` driver automatically.

### 2. Backend (Cloud Run)

Create an env file (for example `env.yaml`, kept out of git):

```yaml
DATABASE_URL: "<neon pooled connection string>"
GROQ_API_KEY: "<key>"
GEMINI_API_KEY: "<key>"
JWT_SECRET_KEY: "<long random secret>"
CORS_ORIGINS: "https://<your-frontend-domain>,http://localhost:5173"
```

Deploy from the `backend/` directory:

```bash
gcloud run deploy llm-gateway --source . \
  --project <project-id> --region us-central1 \
  --allow-unauthenticated \
  --memory 2Gi --cpu 1 \
  --min-instances 0 --max-instances 2 \
  --env-vars-file env.yaml
```

Notes:

- The project needs billing enabled, and the Cloud Run, Cloud Build and Artifact Registry APIs turned on. Usage stays within the free tier at low traffic.
- The default compute service account needs these roles for source builds: `roles/cloudbuild.builds.builder`, `roles/storage.objectViewer`, `roles/artifactregistry.writer`, `roles/logging.logWriter`.
- `backend/.gcloudignore` keeps `venv/` and `.env` out of the upload. The `Dockerfile` must not be listed in it.
- `--env-vars-file` replaces **all** env vars on the service, so always include every variable when updating.
- The Docker image uses CPU-only PyTorch and bakes in the `all-MiniLM-L6-v2` embedding model to keep cold starts short.

### 3. Frontend (Vercel)

From the `frontend/` directory:

```bash
npx vercel deploy --prod --yes \
  -b VITE_API_URL=https://<cloud-run-url> \
  -e VITE_API_URL=https://<cloud-run-url>
```

`frontend/vercel.json` rewrites all paths to `index.html` so React Router routes work on refresh. After the first deploy, add the Vercel domain to `CORS_ORIGINS` on the Cloud Run service.

## API Overview

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/v1/auth/register` | Register a user |
| `POST` | `/v1/auth/token` | Log in and receive a JWT |
| `GET` | `/v1/chats` | List chats for the current user |
| `GET` | `/v1/chats/{chat_id}/messages` | Load messages for a chat |
| `POST` | `/v1/chat` | Send a prompt and receive a streamed response |

## Notes

- The backend does not create database tables automatically.
- The PostgreSQL container should already exist and include `pgvector`.
- API keys should stay in environment variables and should not be committed.
- The embedding model makes the backend image large (about 2.3 GB even with CPU-only PyTorch), so the first request after scale-to-zero is slower.
- Routes that point at unavailable models (for example `groq/compound` or the Gemini Pro model on the free tier) fall back to another model, and the response metadata shows which model actually answered.
