"""
Обработчики для студентов
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from datetime import datetime, date, timedelta
from database.db_sqlserver import (
    get_user, update_user_group, get_schedules_by_group_and_date,
    get_schedules_by_group_and_subject
)
from keyboards.student_keyboards import (
    get_student_main_keyboard, get_subject_search_keyboard
)

router = Router()


class GroupState(StatesGroup):
    waiting_for_group = State()


@router.callback_query(F.data == "student_main")
async def student_main_menu(callback: CallbackQuery):
    """Главное меню студента"""
    user = await get_user(callback.from_user.id)
    if not user or user.get('role') != 'student':
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    group = user.get('user_group')
    text = "👋 <b>Добро пожаловать!</b>\n\n"
    
    if group:
        text += f"Ваша группа: <b>{group}</b>\n\n"
    else:
        text += "⚠️ Сначала укажите вашу группу\n\n"
    
    text += "Выберите действие:"
    
    await callback.message.edit_text(
        text,
        reply_markup=await get_student_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "student_today")
async def student_today_schedule(callback: CallbackQuery):
    """Расписание на сегодня"""
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("❌ Пользователь не найден", show_alert=True)
        return
    
    group = user.get('user_group')
    if not group:
        await callback.message.edit_text(
            "❌ Сначала укажите вашу группу!",
            reply_markup=await get_student_main_keyboard()
        )
        await callback.answer()
        return
    
    today = date.today()
    schedules = await get_schedules_by_group_and_date(group, today)
    
    text = f"📅 <b>Расписание на сегодня ({today.strftime('%d.%m.%Y')})</b>\n\n"
    text += f"Группа: <b>{group}</b>\n\n"
    
    if not schedules:
        text += "❌ Пар на сегодня нет"
    else:
        for schedule in schedules:
            text += f"🕐 {schedule.get('time_start', '')} - {schedule.get('time_end', '')}\n"
            text += f"📖 {schedule.get('subject', '')}\n"
            text += f"🏢 {schedule.get('room', 'Не указана')}\n"
            if schedule.get('teacher_name'):
                text += f"👤 {schedule.get('teacher_name')}\n"
            text += "\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=await get_student_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "student_tomorrow")
async def student_tomorrow_schedule(callback: CallbackQuery):
    """Расписание на завтра"""
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("❌ Пользователь не найден", show_alert=True)
        return
    
    group = user.get('user_group')
    if not group:
        await callback.message.edit_text(
            "❌ Сначала укажите вашу группу!",
            reply_markup=await get_student_main_keyboard()
        )
        await callback.answer()
        return
    
    tomorrow = date.today() + timedelta(days=1)
    schedules = await get_schedules_by_group_and_date(group, tomorrow)
    
    text = f"📅 <b>Расписание на завтра ({tomorrow.strftime('%d.%m.%Y')})</b>\n\n"
    text += f"Группа: <b>{group}</b>\n\n"
    
    if not schedules:
        text += "❌ Пар на завтра нет"
    else:
        for schedule in schedules:
            text += f"🕐 {schedule.get('time_start', '')} - {schedule.get('time_end', '')}\n"
            text += f"📖 {schedule.get('subject', '')}\n"
            text += f"🏢 {schedule.get('room', 'Не указана')}\n"
            if schedule.get('teacher_name'):
                text += f"👤 {schedule.get('teacher_name')}\n"
            text += "\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=await get_student_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "student_by_subject")
async def student_by_subject_start(callback: CallbackQuery, state: FSMContext):
    """Начать поиск по предмету"""
    user = await get_user(callback.from_user.id)
    if not user:
        await callback.answer("❌ Пользователь не найден", show_alert=True)
        return
    
    group = user.get('user_group')
    if not group:
        await callback.message.edit_text(
            "❌ Сначала укажите вашу группу!",
            reply_markup=await get_student_main_keyboard()
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        "🔍 <b>Введите название предмета:</b>\n\n"
        "Например: Математика, Физика, Программирование"
    )
    await state.set_state("waiting_for_subject")
    await callback.answer()


@router.message(F.text, lambda m, state: await state.get_state() == "waiting_for_subject")
async def student_by_subject_search(message: Message, state: FSMContext):
    """Поиск расписания по предмету"""
    user = await get_user(message.from_user.id)
    if not user:
        return
    
    group = user.get('user_group')
    if not group:
        await message.answer("❌ Сначала укажите вашу группу!")
        await state.clear()
        return
    
    subject = message.text.strip()
    schedules = await get_schedules_by_group_and_subject(group, subject)
    
    text = f"📚 <b>Расписание по предмету: {subject}</b>\n\n"
    text += f"Группа: <b>{group}</b>\n\n"
    
    if not schedules:
        text += f"❌ Пар по предмету '{subject}' не найдено"
    else:
        for schedule in schedules:
            text += f"📅 {schedule.get('day_of_week', '')}\n"
            text += f"🕐 {schedule.get('time_start', '')} - {schedule.get('time_end', '')}\n"
            text += f"📖 {schedule.get('subject', '')}\n"
            text += f"🏢 {schedule.get('room', 'Не указана')}\n"
            if schedule.get('teacher_name'):
                text += f"👤 {schedule.get('teacher_name')}\n"
            text += "\n"
    
    await message.answer(
        text,
        reply_markup=await get_student_main_keyboard()
    )
    await state.clear()


@router.callback_query(F.data == "student_change_group")
async def student_change_group_start(callback: CallbackQuery, state: FSMContext):
    """Начать смену группы"""
    user = await get_user(callback.from_user.id)
    current_group = user.get('user_group') if user else None
    
    text = "👥 <b>Введите номер вашей группы:</b>"
    if current_group:
        text += f"\n\nТекущая группа: <b>{current_group}</b>"
    
    await callback.message.edit_text(text)
    await state.set_state(GroupState.waiting_for_group)
    await callback.answer()


@router.message(GroupState.waiting_for_group)
async def student_change_group_process(message: Message, state: FSMContext):
    """Обработка смены группы"""
    user_id = message.from_user.id
    group = message.text.strip()
    
    await update_user_group(user_id, group)
    
    await message.answer(
        f"✅ Группа установлена: <b>{group}</b>",
        reply_markup=await get_student_main_keyboard()
    )
    
    await state.clear()

