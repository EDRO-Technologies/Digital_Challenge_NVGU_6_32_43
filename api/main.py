"""
FastAPI приложение для desktop приложения админа
"""
from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List
from datetime import datetime, date
from pydantic import BaseModel
import logging

from config import API_SECRET_KEY
from database.db_sqlserver import (
    get_teacher_requests, create_request, get_session,
    get_schedules_by_group_and_date, get_teacher_schedules
)
from database.models import RequestStatus, RequestType

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Schedule Admin API", version="1.0.0")

# CORS для desktop приложения
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Pydantic модели
class RequestResponse(BaseModel):
    id: int
    teacher_id: int
    schedule_id: Optional[int]
    request_type: str
    status: str
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class NotificationResponse(BaseModel):
    id: int
    request_id: Optional[int]
    message: str
    status: str
    created_at: datetime


class ScheduleResponse(BaseModel):
    id: int
    specialty: str
    day_of_week: str
    date: Optional[date]
    time_start: str
    time_end: Optional[str]
    subject: str
    teacher_id: Optional[int]
    teacher_name: Optional[str]
    room: Optional[str]
    group_name: Optional[str]


# Зависимость для проверки API ключа
async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_SECRET_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key


@app.get("/")
async def root():
    return {"message": "Schedule Admin API"}


@app.get("/api/requests", response_model=List[RequestResponse])
async def get_requests(
    status: Optional[str] = None,
    teacher_id: Optional[int] = None,
    api_key: str = Depends(verify_api_key)
):
    """Получить список заявок с фильтрацией"""
    # TODO: Реализовать фильтрацию
    return []


@app.get("/api/notifications", response_model=List[NotificationResponse])
async def get_notifications(
    status: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """Получить уведомления админа"""
    # TODO: Реализовать
    return []


@app.post("/api/requests/{request_id}/approve")
async def approve_request(
    request_id: int,
    approved_date: Optional[date] = None,
    approved_time_start: Optional[str] = None,
    approved_room: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """Одобрить заявку"""
    # TODO: Реализовать
    return {"status": "approved"}


@app.post("/api/requests/{request_id}/reject")
async def reject_request(
    request_id: int,
    comment: Optional[str] = None,
    api_key: str = Depends(verify_api_key)
):
    """Отклонить заявку"""
    # TODO: Реализовать
    return {"status": "rejected"}


@app.get("/api/logs")
async def get_admin_logs(
    limit: int = 100,
    api_key: str = Depends(verify_api_key)
):
    """Получить историю действий админа"""
    # TODO: Реализовать
    return []


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

