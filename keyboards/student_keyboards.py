"""Клавиатуры для студентов"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


async def get_student_main_keyboard():
    """Главное меню студента"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📅 Расписание на сегодня", callback_data="student_today")],
        [InlineKeyboardButton(text="📅 Расписание на завтра", callback_data="student_tomorrow")],
        [InlineKeyboardButton(text="🔍 По предмету", callback_data="student_by_subject")],
        [InlineKeyboardButton(text="👥 Изменить группу", callback_data="student_change_group")]
    ])


async def get_subject_search_keyboard():
    """Клавиатура для поиска по предмету"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Назад", callback_data="student_main")]
    ])

