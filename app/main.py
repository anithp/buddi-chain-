"""Main FastAPI application for Buddi Tokenization PoC."""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os

from app.core.config import settings
from app.db.database import engine
from app.db.models import Base
from app.api import conversations, datasets, scheduler

# Create database tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Buddi Tokenization PoC",
    description="A proof-of-concept system for tokenizing user conversation summaries on the æternity blockchain",
    version="1.0.0"
)

# Set up static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Root endpoint with dashboard."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/datasets/", response_class=HTMLResponse)
async def datasets_page(request: Request):
    """Datasets page with table view."""
    return templates.TemplateResponse("datasets.html", {"request": request})


@app.get("/conversations/structured", response_class=HTMLResponse)
async def conversations_structured(request: Request):
    """Structured conversations view with cards and detailed information."""
    return templates.TemplateResponse("conversations_structured.html", {"request": request})


@app.get("/conversations/table", response_class=HTMLResponse)
async def conversations_table(request: Request):
    """Table view of conversations with sorting and filtering."""
    return templates.TemplateResponse("conversations_table.html", {"request": request})


@app.get("/user-dashboard/", response_class=HTMLResponse)
async def user_dashboard(request: Request):
    """User dashboard showing earned tokens from conversations."""
    return templates.TemplateResponse("user_dashboard.html", {"request": request})


# Include API routers (after HTML routes to avoid conflicts)
app.include_router(conversations.router)
app.include_router(datasets.router)
app.include_router(scheduler.router)


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "database": "connected"
    }


@app.get("/api/status")
async def api_status():
    """API status endpoint."""
    return {
        "api_status": "operational",
        "blockchain_network": settings.aeternity_network_id,
        "database_url": settings.database_url.split("://")[0] + "://***",  # Hide credentials
        "buddi_api_configured": bool(settings.buddi_api_key),
        "aeternity_configured": bool(settings.aeternity_private_key)
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
