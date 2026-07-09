from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import interaction

app = FastAPI(
    title="AI First CRM - HCP Module",
    description="AI-powered Healthcare Professional CRM using LangGraph",
    version="1.0.0",
)

# CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(
    interaction.router,
    prefix="/api/interactions",
    tags=["Interactions"],
)


@app.get("/")
async def root():
    return {
        "message": "AI First CRM Backend Running 🚀",
        "status": "success"
    }


@app.get("/health")
async def health():
    return {
        "status": "healthy"
    }