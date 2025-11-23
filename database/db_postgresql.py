"""
Модуль для работы с PostgreSQL базой данных
"""
import asyncpg
import logging
from typing import Optional, List, Dict
from config import (
    POSTGRES_HOST, POSTGRES_PORT, POSTGRES_DATABASE,
    POSTGRES_USER, POSTGRES_PASSWORD
)

logger = logging.getLogger(__name__)

# Глобальный пул соединений
_pool: Optional[asyncpg.Pool] = None


async def get_pool() -> asyncpg.Pool:
    """Получить пул соединений с БД"""
    global _pool
    if _pool is None:
        # Подготовка параметров подключения
        pool_kwargs = {
            'database': POSTGRES_DATABASE,
            'user': POSTGRES_USER,
            'min_size': 2,
            'max_size': 10
        }
        
        # Если пароль указан, добавляем его
        # На macOS через Homebrew обычно пароль не требуется (peer authentication)
        if POSTGRES_PASSWORD and POSTGRES_PASSWORD.strip():
            pool_kwargs['password'] = POSTGRES_PASSWORD
        
        # На macOS через Homebrew PostgreSQL слушает на localhost через TCP/IP
        # Пробуем подключиться через TCP/IP на localhost
        pool_kwargs['host'] = POSTGRES_HOST
        pool_kwargs['port'] = POSTGRES_PORT
        
        try:
            _pool = await asyncpg.create_pool(**pool_kwargs)
            logger.info(f"Подключение к PostgreSQL установлено (user={POSTGRES_USER}, database={POSTGRES_DATABASE})")
        except (asyncpg.exceptions.InvalidPasswordError, asyncpg.exceptions.InvalidCatalogNameError) as e:
            logger.error(f"Ошибка подключения к PostgreSQL: {e}")
            logger.error("Проверьте настройки подключения в config.py или .env файле")
            raise
        except Exception as e:
            logger.error(f"Не удалось подключиться к PostgreSQL: {e}")
            logger.error(f"Убедитесь, что PostgreSQL запущен и доступен на {POSTGRES_HOST}:{POSTGRES_PORT}")
            logger.error("Для запуска PostgreSQL на macOS используйте: brew services start postgresql@14")
            logger.error(f"Попытка подключения с параметрами: user={POSTGRES_USER}, database={POSTGRES_DATABASE}, host={POSTGRES_HOST}, port={POSTGRES_PORT}")
            raise
    return _pool


async def close_pool():
    """Закрыть пул соединений"""
    global _pool
    if _pool:
        await _pool.close()
        _pool = None


async def init_db():
    """Инициализация базы данных и создание таблиц"""
    try:
        pool = await get_pool()
    except Exception as e:
        logger.error(f"Критическая ошибка: не удалось подключиться к базе данных")
        logger.error(f"Детали ошибки: {e}")
        raise
    
    async with pool.acquire() as conn:
        # Таблица пользователей
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id BIGINT PRIMARY KEY,
                role VARCHAR(20) NOT NULL DEFAULT 'student',
                specialty VARCHAR(255),
                user_group VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Добавляем колонку user_group если её нет (для существующих БД)
        try:
            await conn.execute('ALTER TABLE users ADD COLUMN user_group VARCHAR(50)')
        except asyncpg.exceptions.DuplicateColumnError:
            pass  # Колонка уже существует
        
        # Таблица специальностей
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS specialties (
                id SERIAL PRIMARY KEY,
                name VARCHAR(255) NOT NULL UNIQUE,
                code VARCHAR(50)
            )
        ''')
        
        # Таблица расписания
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS schedules (
                id SERIAL PRIMARY KEY,
                specialty VARCHAR(255) NOT NULL,
                semester VARCHAR(50),
                day_of_week VARCHAR(20) NOT NULL,
                time VARCHAR(20) NOT NULL,
                subject VARCHAR(255) NOT NULL,
                teacher VARCHAR(255),
                room VARCHAR(50),
                group_name VARCHAR(50),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        logger.info("База данных PostgreSQL инициализирована успешно")


async def get_user(user_id: int) -> Optional[Dict]:
    """Получить информацию о пользователе"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            'SELECT * FROM users WHERE user_id = $1', user_id
        )
        return dict(row) if row else None


async def add_user(user_id: int, role: str = 'student', specialty: str = None, user_group: str = None):
    """Добавить пользователя"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            '''INSERT INTO users (user_id, role, specialty, user_group) 
               VALUES ($1, $2, $3, $4)
               ON CONFLICT (user_id) DO NOTHING''',
            user_id, role, specialty, user_group
        )


async def update_user_specialty(user_id: int, specialty: str):
    """Обновить специальность пользователя"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            'UPDATE users SET specialty = $1 WHERE user_id = $2',
            specialty, user_id
        )


async def update_user_group(user_id: int, user_group: str):
    """Обновить группу пользователя"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            'UPDATE users SET user_group = $1 WHERE user_id = $2',
            user_group, user_id
        )


async def add_specialty(name: str, code: str = None):
    """Добавить специальность"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            '''INSERT INTO specialties (name, code) 
               VALUES ($1, $2)
               ON CONFLICT (name) DO NOTHING''',
            name, code
        )


async def get_all_specialties() -> List[Dict]:
    """Получить все специальности"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch('SELECT * FROM specialties ORDER BY name')
        return [dict(row) for row in rows]


async def get_specialty_by_id(spec_id: int) -> Optional[Dict]:
    """Получить специальность по ID"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow('SELECT * FROM specialties WHERE id = $1', spec_id)
        return dict(row) if row else None


async def get_specialty_by_name_hash(name: str) -> Optional[Dict]:
    """Получить специальность по названию (fallback)"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow('SELECT * FROM specialties WHERE name = $1', name)
        return dict(row) if row else None


async def add_schedule(specialty: str, day_of_week: str, time: str, subject: str,
                      teacher: str = None, room: str = None, group_name: str = None, semester: str = None):
    """Добавить запись в расписание"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            '''INSERT INTO schedules (specialty, semester, day_of_week, time, subject, teacher, room, group_name)
               VALUES ($1, $2, $3, $4, $5, $6, $7, $8)''',
            specialty, semester, day_of_week, time, subject, teacher, room, group_name
        )


async def get_schedules_by_specialty(specialty: str, day: str = None) -> List[Dict]:
    """Получить расписание по специальности"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        if day:
            rows = await conn.fetch(
                'SELECT * FROM schedules WHERE specialty = $1 AND day_of_week = $2 ORDER BY time',
                specialty, day
            )
        else:
            rows = await conn.fetch(
                'SELECT * FROM schedules WHERE specialty = $1 ORDER BY day_of_week, time',
                specialty
            )
        return [dict(row) for row in rows]


async def search_schedules(query: str, specialty: str = None) -> List[Dict]:
    """Поиск в расписании (регистронезависимый)"""
    query_lower = f'%{query.lower()}%'
    pool = await get_pool()
    async with pool.acquire() as conn:
        if specialty:
            rows = await conn.fetch(
                '''SELECT * FROM schedules 
                   WHERE specialty = $1 AND (LOWER(subject) LIKE $2 OR LOWER(teacher) LIKE $2)
                   ORDER BY day_of_week, time''',
                specialty, query_lower
            )
        else:
            rows = await conn.fetch(
                '''SELECT * FROM schedules 
                   WHERE LOWER(subject) LIKE $1 OR LOWER(teacher) LIKE $1
                   ORDER BY specialty, day_of_week, time''',
                query_lower
            )
        return [dict(row) for row in rows]


async def get_all_schedules() -> List[Dict]:
    """Получить все расписания (для преподавателя)"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        rows = await conn.fetch('SELECT * FROM schedules ORDER BY specialty, day_of_week, time')
        return [dict(row) for row in rows]


async def delete_schedule(schedule_id: int):
    """Удалить запись из расписания"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute('DELETE FROM schedules WHERE id = $1', schedule_id)


async def get_schedule_by_id(schedule_id: int) -> Optional[Dict]:
    """Получить запись расписания по ID"""
    pool = await get_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow('SELECT * FROM schedules WHERE id = $1', schedule_id)
        return dict(row) if row else None


async def update_schedule(schedule_id: int, **kwargs):
    """Обновить запись расписания"""
    allowed_fields = ['specialty', 'semester', 'day_of_week', 'time', 'subject', 'teacher', 'room', 'group_name']
    updates = {k: v for k, v in kwargs.items() if k in allowed_fields and v is not None}
    
    if not updates:
        return
    
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Пересоздаем запрос с правильными плейсхолдерами
        set_parts = []
        params = []
        param_num = 1
        for k, v in updates.items():
            set_parts.append(f'{k} = ${param_num}')
            params.append(v)
            param_num += 1
        set_clause = ', '.join(set_parts)
        params.append(schedule_id)
        
        await conn.execute(
            f'UPDATE schedules SET {set_clause} WHERE id = ${param_num}',
            *params
        )

