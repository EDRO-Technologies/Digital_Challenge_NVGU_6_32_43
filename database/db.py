"""
Модуль для работы с базой данных
Использует PostgreSQL через database/db_postgresql.py
"""
# Импортируем функции из PostgreSQL модуля
from database.db_postgresql import (
    init_db,
    get_user,
    add_user,
    update_user_specialty,
    update_user_group,
    add_specialty,
    get_all_specialties,
    get_specialty_by_id,
    get_specialty_by_name_hash,
    add_schedule,
    get_schedules_by_specialty,
    search_schedules,
    get_all_schedules,
    delete_schedule,
    get_schedule_by_id,
    update_schedule,
    close_pool
)

# Для обратной совместимости, если нужен SQLite, создайте database/db_sqlite.py

