"""
Модуль для работы с SQL Server базой данных
"""
import logging
from typing import Optional, List, Dict
from datetime import datetime, date, time
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from config import SQL_SERVER_CONNECTION_STRING
from database.models import (
    UserRole, RequestStatus, RequestType, NotificationStatus
)

logger = logging.getLogger(__name__)

# Создание асинхронного движка
engine = create_async_engine(
    SQL_SERVER_CONNECTION_STRING,
    echo=False,
    future=True
)

# Создание фабрики сессий
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


async def get_session() -> AsyncSession:
    """Получить сессию БД"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Инициализация базы данных и создание таблиц"""
    from database.models import CREATE_TABLES_SQL
    
    try:
        async with AsyncSessionLocal() as session:
            # Выполняем SQL для создания таблиц
            statements = CREATE_TABLES_SQL.split(';')
            for statement in statements:
                statement = statement.strip()
                if statement:
                    await session.execute(text(statement))
            await session.commit()
            logger.info("База данных инициализирована успешно")
    except Exception as e:
        logger.error(f"Ошибка при инициализации БД: {e}")
        raise


# Функции для работы с пользователями
async def get_user(user_id: int) -> Optional[Dict]:
    """Получить информацию о пользователе"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("SELECT * FROM users WHERE user_id = :user_id"),
            {"user_id": user_id}
        )
        row = result.fetchone()
        if row:
            return dict(row._mapping)
        return None


async def add_user(user_id: int, role: str = 'student', specialty: str = None, 
                   user_group: str = None, teacher_name: str = None):
    """Добавить пользователя"""
    async with AsyncSessionLocal() as session:
        await session.execute(
            text("""
                INSERT INTO users (user_id, role, specialty, user_group, teacher_name)
                VALUES (:user_id, :role, :specialty, :user_group, :teacher_name)
            """),
            {
                "user_id": user_id,
                "role": role,
                "specialty": specialty,
                "user_group": user_group,
                "teacher_name": teacher_name
            }
        )
        await session.commit()


async def update_user_specialty(user_id: int, specialty: str):
    """Обновить специальность пользователя"""
    async with AsyncSessionLocal() as session:
        await session.execute(
            text("UPDATE users SET specialty = :specialty, updated_at = GETDATE() WHERE user_id = :user_id"),
            {"specialty": specialty, "user_id": user_id}
        )
        await session.commit()


async def update_user_group(user_id: int, user_group: str):
    """Обновить группу пользователя"""
    async with AsyncSessionLocal() as session:
        await session.execute(
            text("UPDATE users SET user_group = :user_group, updated_at = GETDATE() WHERE user_id = :user_id"),
            {"user_group": user_group, "user_id": user_id}
        )
        await session.commit()


# Функции для работы с расписанием
async def add_schedule(specialty: str, day_of_week: str, time_start: time, 
                      subject: str, teacher_id: int = None, teacher_name: str = None,
                      room: str = None, group_name: str = None, 
                      time_end: time = None, date: date = None,
                      is_special: bool = False, is_holiday: bool = False):
    """Добавить запись в расписание"""
    async with AsyncSessionLocal() as session:
        await session.execute(
            text("""
                INSERT INTO schedules 
                (specialty, day_of_week, date, time_start, time_end, subject, 
                 teacher_id, teacher_name, room, group_name, is_special, is_holiday)
                VALUES 
                (:specialty, :day_of_week, :date, :time_start, :time_end, :subject,
                 :teacher_id, :teacher_name, :room, :group_name, :is_special, :is_holiday)
            """),
            {
                "specialty": specialty,
                "day_of_week": day_of_week,
                "date": date,
                "time_start": time_start,
                "time_end": time_end,
                "subject": subject,
                "teacher_id": teacher_id,
                "teacher_name": teacher_name,
                "room": room,
                "group_name": group_name,
                "is_special": is_special,
                "is_holiday": is_holiday
            }
        )
        await session.commit()


async def get_schedules_by_group_and_date(group_name: str, target_date: date) -> List[Dict]:
    """Получить расписание для группы на конкретную дату"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT * FROM schedules 
                WHERE group_name = :group_name 
                AND (date = :date OR (date IS NULL AND day_of_week = DATENAME(WEEKDAY, :date)))
                AND is_holiday = 0
                ORDER BY time_start
            """),
            {"group_name": group_name, "date": target_date}
        )
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]


async def get_schedules_by_group_and_subject(group_name: str, subject: str) -> List[Dict]:
    """Получить расписание для группы по предмету"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT * FROM schedules 
                WHERE group_name = :group_name 
                AND LOWER(subject) LIKE LOWER(:subject)
                ORDER BY day_of_week, time_start
            """),
            {"group_name": group_name, "subject": f"%{subject}%"}
        )
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]


async def get_teacher_schedules(teacher_id: int) -> List[Dict]:
    """Получить расписание преподавателя"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT * FROM schedules 
                WHERE teacher_id = :teacher_id
                ORDER BY day_of_week, time_start
            """),
            {"teacher_id": teacher_id}
        )
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]


# Функции для работы с заявками
async def create_request(teacher_id: int, schedule_id: int, request_type: str,
                        reason: str, **kwargs) -> int:
    """Создать заявку от преподавателя"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                INSERT INTO requests 
                (teacher_id, schedule_id, request_type, status, reason,
                 original_date, original_time_start, original_time_end, original_room,
                 preferred_date_1, preferred_time_1_start, preferred_time_1_end, preferred_room_1,
                 preferred_date_2, preferred_time_2_start, preferred_time_2_end, preferred_room_2,
                 preferred_date_3, preferred_time_3_start, preferred_time_3_end, preferred_room_3)
                VALUES 
                (:teacher_id, :schedule_id, :request_type, 'pending', :reason,
                 :original_date, :original_time_start, :original_time_end, :original_room,
                 :preferred_date_1, :preferred_time_1_start, :preferred_time_1_end, :preferred_room_1,
                 :preferred_date_2, :preferred_time_2_start, :preferred_time_2_end, :preferred_room_2,
                 :preferred_date_3, :preferred_time_3_start, :preferred_time_3_end, :preferred_room_3)
                SELECT SCOPE_IDENTITY() AS id
            """),
            {
                "teacher_id": teacher_id,
                "schedule_id": schedule_id,
                "request_type": request_type,
                "reason": reason,
                **kwargs
            }
        )
        request_id = result.scalar()
        await session.commit()
        
        # Создаем уведомление для админа
        await create_notification(ADMIN_ID, request_id, 
                                  f"Новая заявка от преподавателя")
        
        return request_id


async def create_notification(admin_id: int, request_id: int, message: str):
    """Создать уведомление для админа"""
    async with AsyncSessionLocal() as session:
        await session.execute(
            text("""
                INSERT INTO notifications (admin_id, request_id, message, status)
                VALUES (:admin_id, :request_id, :message, 'unread')
            """),
            {"admin_id": admin_id, "request_id": request_id, "message": message}
        )
        await session.commit()


async def get_teacher_requests(teacher_id: int) -> List[Dict]:
    """Получить заявки преподавателя"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            text("""
                SELECT * FROM requests 
                WHERE teacher_id = :teacher_id
                ORDER BY created_at DESC
            """),
            {"teacher_id": teacher_id}
        )
        rows = result.fetchall()
        return [dict(row._mapping) for row in rows]


# Импорт ADMIN_ID из config
from config import ADMIN_ID

