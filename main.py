import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from config import BOT_TOKEN
from database.db import init_db, close_pool
from handlers import start_router, student_router, teacher_router, unknown_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """Основная функция запуска бота"""
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN не установлен! Установите его в .env файле или config.py")
        return
    
    # Инициализация базы данных
    logger.info("Инициализация базы данных...")
    await init_db()
    logger.info("База данных инициализирована")
    
    # Автоматическая загрузка специальностей из Excel файлов при первом запуске
    from database.db import get_all_specialties
    specialties = await get_all_specialties()
    if not specialties:
        logger.info("Специальности не найдены, загружаем из Excel файлов...")
        from utils.excel_parser import load_all_excel_files
        await load_all_excel_files()
        logger.info("Загрузка Excel файлов завершена")
    
    # Создание бота и диспетчера
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher()
    
    # Регистрация роутеров (unknown_router должен быть последним)
    dp.include_router(start_router)
    dp.include_router(student_router)
    dp.include_router(teacher_router)
    dp.include_router(unknown_router)
    
    logger.info("Бот запущен")
    
    # Запуск бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен")
    finally:
        # Закрываем пул соединений с БД
        try:
            asyncio.run(close_pool())
            logger.info("Пул соединений с БД закрыт")
        except Exception as e:
            logger.error(f"Ошибка при закрытии пула соединений: {e}")

