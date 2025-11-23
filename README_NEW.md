# Система управления расписанием

Комплексная система управления расписанием с тремя ролями: Админ, Преподаватель, Студент.

## Структура проекта

```
project/
├── api/                    # FastAPI для desktop приложения
│   └── main.py
├── database/               # Работа с БД
│   ├── models.py          # Модели данных
│   └── db_sqlserver.py    # Функции работы с SQL Server
├── desktop_app/            # Desktop приложение для админа
│   └── main.py
├── handlers/               # Обработчики Telegram бота
│   ├── teacher_handlers_new.py
│   └── student_handlers_new.py
├── keyboards/             # Клавиатуры
│   ├── teacher_keyboards.py
│   └── student_keyboards.py
├── utils/                 # Утилиты
│   └── excel_parser.py
└── main.py               # Точка входа Telegram бота
```

## Установка и настройка

### 1. Установка зависимостей

```bash
pip install -r requirements.txt
```

### 2. Настройка SQL Server

1. Установите SQL Server
2. Создайте базу данных
3. Настройте ODBC драйвер для SQL Server
4. Обновите `.env` файл:

```env
SQL_SERVER_HOST=localhost
SQL_SERVER_PORT=1433
SQL_SERVER_DATABASE=schedule_db
SQL_SERVER_USER=sa
SQL_SERVER_PASSWORD=YourPassword123!
```

### 3. Настройка Telegram бота

```env
BOT_TOKEN=your_bot_token
ADMIN_ID=your_telegram_id
```

### 4. Настройка API

```env
API_HOST=localhost
API_PORT=8000
API_SECRET_KEY=your-secret-key
```

## Запуск

### Telegram бот

```bash
python main.py
```

### API сервер

```bash
python api/main.py
# или
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

### Desktop приложение

```bash
python desktop_app/main.py
```

## Роли и функции

### Админ (Desktop приложение)

- Загрузка расписания из Excel
- Рассмотрение заявок от преподавателей
- Перенос/отмена пар
- Изменение аудиторий
- Управление преподавателями
- Просмотр истории действий
- Управление особыми днями (выходные, короткие дни)

### Преподаватель (Telegram бот)

- Просмотр своих пар
- Создание заявок на:
  - Отмену пары
  - Перенос пары (с указанием альтернативных вариантов)
  - Изменение аудитории
- Указание причины заявки
- Просмотр статуса своих заявок

### Студент (Telegram бот)

- Просмотр расписания на сегодня
- Просмотр расписания на завтра
- Поиск расписания по предмету
- Изменение своей группы

## База данных

Система использует Microsoft SQL Server со следующими основными таблицами:

- `users` - пользователи (админы, преподаватели, студенты)
- `schedules` - расписание
- `requests` - заявки от преподавателей
- `notifications` - уведомления для админа
- `admin_logs` - история действий админа
- `special_days` - особые дни (выходные, короткие дни)

## API Endpoints

- `GET /api/requests` - Получить список заявок
- `GET /api/notifications` - Получить уведомления
- `POST /api/requests/{id}/approve` - Одобрить заявку
- `POST /api/requests/{id}/reject` - Отклонить заявку
- `GET /api/logs` - Получить историю действий

Все запросы требуют заголовок `X-API-Key` с секретным ключом.

## Примечания

- Для работы с SQL Server необходим ODBC драйвер
- Desktop приложение требует PyQt6
- API использует FastAPI и требует запуска отдельного сервера

