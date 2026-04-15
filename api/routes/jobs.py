# api/routes/jobs.py
# Job status endpoints

from fastapi import APIRouter, HTTPException
from api.models import JobStatusResponse, JobListResponse
from services.job_queue import get_job_queue

router = APIRouter()


@router.get("/{job_id}", response_model=JobStatusResponse)
async def get_job_status(job_id: str):
    """Get status of a specific job."""
    job_queue = get_job_queue()
    job = job_queue.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    return JobStatusResponse(**job)


@router.get("", response_model=JobListResponse)
async def list_jobs(status: str = None):
    """List all jobs, optionally filtered by status."""
    job_queue = get_job_queue()
    jobs = job_queue.get_all_jobs()
    
    if status:
        jobs = [j for j in jobs if j["status"] == status]
    
    return JobListResponse(
        jobs=[JobStatusResponse(**j) for j in jobs],
        count=len(jobs)
    )


@router.post("/{job_id}/cancel")
async def cancel_job(job_id: str):
    """Cancel a pending job."""
    job_queue = get_job_queue()
    job = job_queue.get_job(job_id)
    
    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")
    
    success = job_queue.cancel_job(job_id)
    
    if success:
        return {"status": "ok", "message": f"Job {job_id} cancelled"}
    else:
        raise HTTPException(
            status_code=400, 
            detail=f"Cannot cancel job - status is {job['status']}"
        )
