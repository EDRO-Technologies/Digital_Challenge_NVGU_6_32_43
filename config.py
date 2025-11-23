import os
from dotenv import load_dotenv

load_dotenv()

# ID администратора (прописать свой Telegram ID)
ADMIN_ID = int(os.getenv('ADMIN_ID', '814963372'))  # Замените на реальный ID

# Для обратной совместимости со старым кодом
TEACHER_ID = ADMIN_ID  # В старой версии использовался TEACHER_ID

# Токен бота
BOT_TOKEN = os.getenv('BOT_TOKEN', '8542970294:AAGkl61iJhG2F0A5f1MjsNAuKkcINS-OK3k')

# Путь к базе данных SQLite (для обратной совместимости со старым кодом)
DB_PATH = os.getenv('DB_PATH', 'schedule_bot.db')

# Настройки PostgreSQL
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_PORT = int(os.getenv('POSTGRES_PORT', '5432'))
POSTGRES_DATABASE = os.getenv('POSTGRES_DATABASE', 'schedule_db')
# На macOS через Homebrew обычно используется текущий пользователь системы
POSTGRES_USER = os.getenv('POSTGRES_USER', os.getenv('USER', 'postgres'))
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD', '')  # На macOS обычно пароль не требуется

# Строка подключения к PostgreSQL
POSTGRES_CONNECTION_STRING = (
    f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@"
    f"{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
)

# Настройки SQL Server (для обратной совместимости)
SQL_SERVER_HOST = os.getenv('SQL_SERVER_HOST', 'localhost')
SQL_SERVER_PORT = os.getenv('SQL_SERVER_PORT', '1433')
SQL_SERVER_DATABASE = os.getenv('SQL_SERVER_DATABASE', 'schedule_db')
SQL_SERVER_USER = os.getenv('SQL_SERVER_USER', 'sa')
SQL_SERVER_PASSWORD = os.getenv('SQL_SERVER_PASSWORD', 'YourPassword123!')

# Строка подключения к SQL Server
SQL_SERVER_CONNECTION_STRING = (
    f"mssql+aioodbc://{SQL_SERVER_USER}:{SQL_SERVER_PASSWORD}@"
    f"{SQL_SERVER_HOST}:{SQL_SERVER_PORT}/{SQL_SERVER_DATABASE}?"
    f"driver=ODBC+Driver+17+for+SQL+Server"
)

# Пути к папкам с Excel файлами
EXCEL_FOLDER_1 = '1'
EXCEL_FOLDER_2 = '2'

# Настройки API для desktop приложения
API_HOST = os.getenv('API_HOST', 'localhost')
API_PORT = int(os.getenv('API_PORT', '8000'))
API_SECRET_KEY = os.getenv('API_SECRET_KEY', 'your-secret-key-change-in-production')
