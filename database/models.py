"""
Модели базы данных для системы расписания
"""
from datetime import datetime
from typing import Optional
from enum import Enum


class UserRole(str, Enum):
    """Роли пользователей"""
    ADMIN = "admin"
    TEACHER = "teacher"
    STUDENT = "student"


class RequestStatus(str, Enum):
    """Статусы заявок"""
    PENDING = "pending"  # На рассмотрении
    APPROVED = "approved"  # Принята
    REJECTED = "rejected"  # Отклонена


class RequestType(str, Enum):
    """Типы заявок"""
    CANCEL = "cancel"  # Отмена пары
    RESCHEDULE = "reschedule"  # Перенос пары
    CHANGE_ROOM = "change_room"  # Изменение аудитории


class NotificationStatus(str, Enum):
    """Статусы уведомлений"""
    UNREAD = "unread"
    READ = "read"


# SQL схемы для создания таблиц
CREATE_TABLES_SQL = """
-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    role VARCHAR(20) NOT NULL DEFAULT 'student',
    specialty VARCHAR(255),
    user_group VARCHAR(50),
    teacher_name VARCHAR(255),
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE()
);

-- Таблица специальностей
CREATE TABLE IF NOT EXISTS specialties (
    id INT IDENTITY(1,1) PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    code VARCHAR(50)
);

-- Таблица расписания
CREATE TABLE IF NOT EXISTS schedules (
    id INT IDENTITY(1,1) PRIMARY KEY,
    specialty VARCHAR(255) NOT NULL,
    semester VARCHAR(50),
    day_of_week VARCHAR(20) NOT NULL,
    date DATE,  -- Конкретная дата (для особых расписаний)
    time_start TIME NOT NULL,
    time_end TIME,
    subject VARCHAR(255) NOT NULL,
    teacher_id BIGINT,
    teacher_name VARCHAR(255),
    room VARCHAR(50),
    group_name VARCHAR(50),
    is_special BOOLEAN DEFAULT 0,  -- Особое расписание
    is_holiday BOOLEAN DEFAULT 0,  -- Выходной день
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (teacher_id) REFERENCES users(user_id)
);

-- Таблица заявок от преподавателей
CREATE TABLE IF NOT EXISTS requests (
    id INT IDENTITY(1,1) PRIMARY KEY,
    teacher_id BIGINT NOT NULL,
    schedule_id INT,
    request_type VARCHAR(20) NOT NULL,  -- cancel, reschedule, change_room
    status VARCHAR(20) DEFAULT 'pending',  -- pending, approved, rejected
    reason TEXT,
    original_date DATE,
    original_time_start TIME,
    original_time_end TIME,
    original_room VARCHAR(50),
    -- Для переноса
    preferred_date_1 DATE,
    preferred_time_1_start TIME,
    preferred_time_1_end TIME,
    preferred_room_1 VARCHAR(50),
    preferred_date_2 DATE,
    preferred_time_2_start TIME,
    preferred_time_2_end TIME,
    preferred_room_2 VARCHAR(50),
    preferred_date_3 DATE,
    preferred_time_3_start TIME,
    preferred_time_3_end TIME,
    preferred_room_3 VARCHAR(50),
    -- Результат
    approved_date DATE,
    approved_time_start TIME,
    approved_time_end TIME,
    approved_room VARCHAR(50),
    admin_comment TEXT,
    created_at DATETIME DEFAULT GETDATE(),
    updated_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (teacher_id) REFERENCES users(user_id),
    FOREIGN KEY (schedule_id) REFERENCES schedules(id)
);

-- Таблица уведомлений
CREATE TABLE IF NOT EXISTS notifications (
    id INT IDENTITY(1,1) PRIMARY KEY,
    admin_id BIGINT NOT NULL,
    request_id INT,
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'unread',  -- unread, read
    created_at DATETIME DEFAULT GETDATE(),
    read_at DATETIME,
    FOREIGN KEY (admin_id) REFERENCES users(user_id),
    FOREIGN KEY (request_id) REFERENCES requests(id)
);

-- Таблица истории действий админа
CREATE TABLE IF NOT EXISTS admin_logs (
    id INT IDENTITY(1,1) PRIMARY KEY,
    admin_id BIGINT NOT NULL,
    action_type VARCHAR(50) NOT NULL,  -- schedule_change, request_approved, etc.
    description TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (admin_id) REFERENCES users(user_id)
);

-- Таблица особых дней (выходные, короткие дни)
CREATE TABLE IF NOT EXISTS special_days (
    id INT IDENTITY(1,1) PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    is_holiday BOOLEAN DEFAULT 0,
    is_short_day BOOLEAN DEFAULT 0,
    description TEXT,
    created_at DATETIME DEFAULT GETDATE(),
    created_by BIGINT,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_schedules_date ON schedules(date);
CREATE INDEX IF NOT EXISTS idx_schedules_teacher ON schedules(teacher_id);
CREATE INDEX IF NOT EXISTS idx_requests_status ON requests(status);
CREATE INDEX IF NOT EXISTS idx_requests_teacher ON requests(teacher_id);
CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);
"""

# SQL схемы для PostgreSQL
CREATE_TABLES_SQL_POSTGRESQL = """
-- Таблица пользователей
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    role VARCHAR(20) NOT NULL DEFAULT 'student',
    specialty VARCHAR(255),
    user_group VARCHAR(50),
    teacher_name VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Таблица специальностей
CREATE TABLE IF NOT EXISTS specialties (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE,
    code VARCHAR(50)
);

-- Таблица расписания
CREATE TABLE IF NOT EXISTS schedules (
    id SERIAL PRIMARY KEY,
    specialty VARCHAR(255) NOT NULL,
    semester VARCHAR(50),
    day_of_week VARCHAR(20) NOT NULL,
    date DATE,  -- Конкретная дата (для особых расписаний)
    time_start TIME,
    time_end TIME,
    time VARCHAR(20),  -- Для обратной совместимости
    subject VARCHAR(255) NOT NULL,
    teacher_id BIGINT,
    teacher_name VARCHAR(255),
    room VARCHAR(50),
    group_name VARCHAR(50),
    is_special BOOLEAN DEFAULT FALSE,  -- Особое расписание
    is_holiday BOOLEAN DEFAULT FALSE,  -- Выходной день
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES users(user_id)
);

-- Таблица заявок от преподавателей
CREATE TABLE IF NOT EXISTS requests (
    id SERIAL PRIMARY KEY,
    teacher_id BIGINT NOT NULL,
    schedule_id INTEGER,
    request_type VARCHAR(20) NOT NULL,  -- cancel, reschedule, change_room
    status VARCHAR(20) DEFAULT 'pending',  -- pending, approved, rejected
    reason TEXT,
    original_date DATE,
    original_time_start TIME,
    original_time_end TIME,
    original_room VARCHAR(50),
    -- Для переноса
    preferred_date_1 DATE,
    preferred_time_1_start TIME,
    preferred_time_1_end TIME,
    preferred_room_1 VARCHAR(50),
    preferred_date_2 DATE,
    preferred_time_2_start TIME,
    preferred_time_2_end TIME,
    preferred_room_2 VARCHAR(50),
    preferred_date_3 DATE,
    preferred_time_3_start TIME,
    preferred_time_3_end TIME,
    preferred_room_3 VARCHAR(50),
    -- Результат
    approved_date DATE,
    approved_time_start TIME,
    approved_time_end TIME,
    approved_room VARCHAR(50),
    admin_comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (teacher_id) REFERENCES users(user_id),
    FOREIGN KEY (schedule_id) REFERENCES schedules(id)
);

-- Таблица уведомлений
CREATE TABLE IF NOT EXISTS notifications (
    id SERIAL PRIMARY KEY,
    admin_id BIGINT NOT NULL,
    request_id INTEGER,
    message TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'unread',  -- unread, read
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    read_at TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(user_id),
    FOREIGN KEY (request_id) REFERENCES requests(id)
);

-- Таблица истории действий админа
CREATE TABLE IF NOT EXISTS admin_logs (
    id SERIAL PRIMARY KEY,
    admin_id BIGINT NOT NULL,
    action_type VARCHAR(50) NOT NULL,  -- schedule_change, request_approved, etc.
    description TEXT NOT NULL,
    old_value TEXT,
    new_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (admin_id) REFERENCES users(user_id)
);

-- Таблица особых дней (выходные, короткие дни)
CREATE TABLE IF NOT EXISTS special_days (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL UNIQUE,
    is_holiday BOOLEAN DEFAULT FALSE,
    is_short_day BOOLEAN DEFAULT FALSE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_by BIGINT,
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

-- Индексы для оптимизации
CREATE INDEX IF NOT EXISTS idx_schedules_date ON schedules(date);
CREATE INDEX IF NOT EXISTS idx_schedules_teacher ON schedules(teacher_id);
CREATE INDEX IF NOT EXISTS idx_requests_status ON requests(status);
CREATE INDEX IF NOT EXISTS idx_requests_teacher ON requests(teacher_id);
CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);
"""

