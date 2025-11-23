from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from config import TEACHER_ID
from database.db import get_user, add_user
from keyboards.inline import get_main_menu_keyboard

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    
    # Проверяем, является ли пользователь преподавателем
    is_teacher = user_id == TEACHER_ID
    
    # Получаем или создаем пользователя
    user = await get_user(user_id)
    if not user:
        await add_user(user_id, role='teacher' if is_teacher else 'student')
    
    if is_teacher:
        text = "👋 Добро пожаловать, преподаватель!\n\n"
        text += "Вы можете:\n"
        text += "• Добавлять и редактировать расписание\n"
        text += "• Загружать Excel файлы\n"
        text += "• Управлять специальностями\n"
        text += "• Просматривать все расписания"
    else:
        text = "👋 Добро пожаловать!\n\n"
        text += "Я помогу вам узнать расписание занятий.\n\n"
        text += "Выберите специальность и получите актуальное расписание."
    
    await message.answer(
        text,
        reply_markup=await get_main_menu_keyboard(is_teacher=is_teacher)
    )

