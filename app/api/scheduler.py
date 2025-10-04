"""API routes for scheduler management."""

from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
from app.services.scheduler import scheduler

router = APIRouter(prefix="/api/scheduler", tags=["scheduler"])


class SchedulerStatusResponse(BaseModel):
    """Response model for scheduler status."""
    is_running: bool
    last_fetch_time: str = None
    fetch_interval_hours: int
    max_conversations_per_fetch: int


class ManualFetchResponse(BaseModel):
    """Response model for manual fetch."""
    success: bool
    message: str


@router.get("/status", response_model=SchedulerStatusResponse)
async def get_scheduler_status():
    """Get current scheduler status."""
    status = scheduler.get_status()
    return SchedulerStatusResponse(**status)


@router.post("/start")
async def start_scheduler(background_tasks: BackgroundTasks):
    """Start the conversation scheduler."""
    if scheduler.is_running:
        return {"success": False, "message": "Scheduler is already running"}
    
    background_tasks.add_task(scheduler.start_scheduler)
    return {"success": True, "message": "Scheduler started successfully"}


@router.post("/stop")
async def stop_scheduler():
    """Stop the conversation scheduler."""
    if not scheduler.is_running:
        return {"success": False, "message": "Scheduler is not running"}
    
    await scheduler.stop_scheduler()
    return {"success": True, "message": "Scheduler stopped successfully"}


@router.post("/fetch", response_model=ManualFetchResponse)
async def manual_fetch():
    """Manually trigger a conversation fetch."""
    try:
        await scheduler.run_manual_fetch()
        return ManualFetchResponse(
            success=True,
            message="Manual fetch completed successfully"
        )
    except Exception as e:
        return ManualFetchResponse(
            success=False,
            message=f"Manual fetch failed: {str(e)}"
        )


@router.post("/config")
async def update_scheduler_config(
    fetch_interval_hours: int = None,
    max_conversations_per_fetch: int = None
):
    """Update scheduler configuration."""
    if fetch_interval_hours is not None:
        if 1 <= fetch_interval_hours <= 24:
            scheduler.fetch_interval_hours = fetch_interval_hours
        else:
            return {"success": False, "message": "Fetch interval must be between 1 and 24 hours"}
    
    if max_conversations_per_fetch is not None:
        if 1 <= max_conversations_per_fetch <= 1000:
            scheduler.max_conversations_per_fetch = max_conversations_per_fetch
        else:
            return {"success": False, "message": "Max conversations must be between 1 and 1000"}
    
    return {
        "success": True,
        "message": "Configuration updated successfully",
        "config": scheduler.get_status()
    }
