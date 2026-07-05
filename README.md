# Adaptive LLM Gateway

An adaptive FastAPI + React application that routes chat requests across multiple LLM providers based on prompt type, capability, and fallback behavior. The project uses PostgreSQL with `pgvector` for route prototype embeddings, JWT authentication for users, and a streaming chat UI built with React and Vite.

> Deployment note: this project is not hosted publicly because the backend depends on heavier ML/runtime dependencies such as `sentence-transformers` and provider SDKs. Screenshots are included instead of a live demo.

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
```

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

Run it on the same Docker network as the existing PostgreSQL container:

```bash
docker run --name llm_gateway_backend --rm \
  --network <db-network-name> \
  -p 8000:8000 \
  --env-file backend/.env \
  -e DATABASE_URL=postgresql://postgres:postgres@llm_gateway_db:5432/llm_gateway \
  llm-gateway-backend
```

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
- The model embedding dependency can make the backend image large, which is why screenshots are used for showcasing the project.
