"""Клавиатуры для преподавателей"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def get_teacher_main_keyboard():
    """Главное меню преподавателя"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Мои пары", callback_data="teacher_my_schedules")],
        [InlineKeyboardButton(text="📝 Создать заявку", callback_data="teacher_create_request")],
        [InlineKeyboardButton(text="📋 Мои заявки", callback_data="teacher_my_requests")]
    ])


async def get_request_type_keyboard():
    """Клавиатура выбора типа заявки"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена пары", callback_data="request_type_cancel")],
        [InlineKeyboardButton(text="🔄 Перенос пары", callback_data="request_type_reschedule")],
        [InlineKeyboardButton(text="🏢 Изменить аудиторию", callback_data="request_type_change_room")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="teacher_main")]
    ])


async def get_my_requests_keyboard():
    """Клавиатура для просмотра заявок"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="teacher_main")]
    ])

