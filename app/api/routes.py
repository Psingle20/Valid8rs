from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.responses import StreamingResponse
from typing import Dict
from uuid import uuid4
from datetime import datetime
import asyncio

from .models import TextCheckRequest, TweetCheckRequest, CheckResponse
from .dependencies import get_fact_checker, get_check_results
from ..utils.logging import get_logger, log_queue

MAX_TEXT_LENGTH = 300

def truncate_text(text):
    return text[:MAX_TEXT_LENGTH]

logger = get_logger("fact_checker.api.routes")
router = APIRouter()

@router.post("/check/text", response_model=CheckResponse)
async def check_text(
    request: TextCheckRequest,
    background_tasks: BackgroundTasks,
    fact_checker = Depends(get_fact_checker),
    check_results: Dict = Depends(get_check_results)
):
    check_id = str(uuid4())
    logger.info(f"Starting text check {check_id}")
    
    check_results[check_id] = {
        "check_id": check_id,
        "status": "pending",
        "started_at": datetime.utcnow()
    }

    config = {"text": truncate_text(request.text)}
    
    try:
        if request.background_check:
            background_tasks.add_task(
                fact_checker.run_check,
                check_id,
                config,
                check_results
            )
            logger.info(f"Background check {check_id} initiated")
        else:
            await fact_checker.run_check(check_id, config, check_results)
            logger.info(f"Synchronous check {check_id} completed")

        return CheckResponse(**check_results[check_id])
    except Exception as e:
        logger.error(f"Error in check_text {check_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/check/tweet", response_model=CheckResponse)
async def check_tweet(
    request: TweetCheckRequest,
    background_tasks: BackgroundTasks,
    fact_checker = Depends(get_fact_checker),
    check_results: Dict = Depends(get_check_results)
):
    check_id = str(uuid4())
    logger.info(f"Starting tweet check {check_id} for tweet {request.tweet_id}")
    
    check_results[check_id] = {
        "check_id": check_id,
        "status": "pending",
        "started_at": datetime.utcnow()
    }

    config = {"tweet_id": request.tweet_id}

    try:
        if request.background_check:
            background_tasks.add_task(
                fact_checker.run_check,
                check_id,
                config,
                check_results
            )
            await fact_checker.run_check(check_id, config, check_results)

            logger.info(f"Background check {check_id} initiated")
        else:
            await fact_checker.run_check(check_id, config, check_results)
            logger.info(f"Synchronous check {check_id} completed")

        return CheckResponse(**check_results[check_id])
    except Exception as e:
        logger.error(f"Error in check_tweet {check_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/logs")
async def stream_logs():
    """Stream logs in real-time using SSE"""
    async def event_generator():
        while True:
            try:
                log = log_queue.get_nowait()  # Get log from queue
                yield f"data: {log}\n\n"
            except asyncio.QueueEmpty:
                await asyncio.sleep(0.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
