from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime
from database.db import get_user, update_user_specialty, update_user_group, get_schedules_by_specialty, search_schedules
from keyboards.inline import get_specialties_keyboard, get_days_keyboard, get_main_menu_keyboard
from utils.formatters import format_schedules_list
from config import TEACHER_ID

router = Router()


class SearchState(StatesGroup):
    waiting_for_query = State()


class GroupState(StatesGroup):
    waiting_for_group = State()


@router.callback_query(F.data == "choose_specialty")
async def choose_specialty(callback: CallbackQuery):
    """Выбор специальности (только для студентов)"""
    user_id = callback.from_user.id
    is_teacher = user_id == TEACHER_ID
    
    # Преподаватели не должны использовать эту команду
    if is_teacher:
        await callback.answer("❌ Преподаватели используют меню управления для просмотра расписания", show_alert=True)
        return
    
    keyboard = await get_specialties_keyboard(show_back=True)
    text = "📚 Выберите вашу специальность:"
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data.startswith("spec_"))
async def set_specialty(callback: CallbackQuery):
    """Установка специальности для пользователя"""
    from database.db import get_specialty_by_id
    
    # Получаем ID из callback_data
    spec_id_str = callback.data.replace("spec_", "")
    try:
        spec_id = int(spec_id_str)
    except ValueError:
        await callback.answer("❌ Ошибка: неверный ID специальности", show_alert=True)
        return
    
    # Получаем специальность по ID
    spec = await get_specialty_by_id(spec_id)
    if not spec:
        await callback.answer("❌ Специальность не найдена", show_alert=True)
        return
    
    specialty_name = spec['name']
    user_id = callback.from_user.id
    is_teacher = user_id == TEACHER_ID
    
    if is_teacher:
        # Для преподавателя просто показываем расписание выбранной специальности
        schedules = await get_schedules_by_specialty(specialty_name)
        text = f"📋 <b>Расписание для специальности: {specialty_name}</b>\n\n"
        text += format_schedules_list(schedules, "")
        
        await callback.message.edit_text(
            text,
            reply_markup=await get_main_menu_keyboard(is_teacher=True)
        )
    else:
        # Для студентов устанавливаем специальность
        await update_user_specialty(user_id, specialty_name)
        
        await callback.message.edit_text(
            f"✅ Специальность установлена: <b>{specialty_name}</b>\n\n"
            "Теперь вы можете просматривать расписание.",
            reply_markup=await get_main_menu_keyboard(is_teacher=False)
        )
    
    await callback.answer()


@router.callback_query(F.data == "today_schedule")
async def today_schedule(callback: CallbackQuery):
    """Расписание на сегодня"""
    user_id = callback.from_user.id
    user = await get_user(user_id)
    
    if not user or not user.get('specialty'):
        await callback.message.edit_text(
            "❌ Сначала выберите специальность!",
            reply_markup=await get_main_menu_keyboard(is_teacher=(user_id == TEACHER_ID))
        )
        await callback.answer()
        return
    
    # Определяем день недели
    days = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']
    today = datetime.now().weekday()
    day_name = days[today]
    
    schedules = await get_schedules_by_specialty(user['specialty'], day_name)
    
    text = f"📅 <b>Расписание на сегодня ({day_name})</b>\n"
    text += f"Специальность: {user['specialty']}\n\n"
    text += format_schedules_list(schedules, "")
    
    await callback.message.edit_text(
        text,
        reply_markup=await get_main_menu_keyboard(is_teacher=(user_id == TEACHER_ID))
    )
    await callback.answer()


@router.callback_query(F.data == "week_schedule")
async def week_schedule(callback: CallbackQuery):
    """Расписание на неделю"""
    user_id = callback.from_user.id
    user = await get_user(user_id)
    
    if not user or not user.get('specialty'):
        await callback.message.edit_text(
            "❌ Сначала выберите специальность!",
            reply_markup=await get_main_menu_keyboard(is_teacher=(user_id == TEACHER_ID))
        )
        await callback.answer()
        return
    
    await callback.message.edit_text(
        "📅 Выберите день недели:",
        reply_markup=get_days_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data.startswith("day_"))
async def day_schedule(callback: CallbackQuery):
    """Расписание на выбранный день"""
    user_id = callback.from_user.id
    user = await get_user(user_id)
    
    if not user or not user.get('specialty'):
        await callback.message.edit_text(
            "❌ Сначала выберите специальность!",
            reply_markup=await get_main_menu_keyboard(is_teacher=(user_id == TEACHER_ID))
        )
        await callback.answer()
        return
    
    day_param = callback.data.replace("day_", "")
    
    if day_param == "all":
        schedules = await get_schedules_by_specialty(user['specialty'])
        day_name = "Вся неделя"
    else:
        schedules = await get_schedules_by_specialty(user['specialty'], day_param)
        day_name = day_param
    
    text = f"📅 <b>Расписание на {day_name}</b>\n"
    text += f"Специальность: {user['specialty']}\n\n"
    text += format_schedules_list(schedules, "")
    
    await callback.message.edit_text(
        text,
        reply_markup=await get_main_menu_keyboard(is_teacher=(user_id == TEACHER_ID))
    )
    await callback.answer()


@router.callback_query(F.data == "search_schedule")
async def start_search(callback: CallbackQuery, state: FSMContext):
    """Начать поиск"""
    await callback.message.edit_text(
        "🔍 Введите название предмета или имя преподавателя для поиска:"
    )
    await state.set_state(SearchState.waiting_for_query)
    await callback.answer()


@router.message(SearchState.waiting_for_query)
async def process_search(message: Message, state: FSMContext):
    """Обработка поискового запроса"""
    user_id = message.from_user.id
    user = await get_user(user_id)
    
    query = message.text
    
    if user and user.get('specialty'):
        schedules = await search_schedules(query, user['specialty'])
    else:
        schedules = await search_schedules(query)
    
    if schedules:
        text = f"🔍 <b>Результаты поиска по запросу: {query}</b>\n\n"
        text += format_schedules_list(schedules, "")
    else:
        text = f"❌ По запросу '{query}' ничего не найдено"
    
    await message.answer(
        text,
        reply_markup=await get_main_menu_keyboard(is_teacher=(user_id == TEACHER_ID))
    )
    
    await state.clear()


@router.callback_query(F.data == "main_menu")
async def back_to_main(callback: CallbackQuery):
    """Вернуться в главное меню"""
    user_id = callback.from_user.id
    is_teacher = user_id == TEACHER_ID
    
    text = "🏠 Главное меню"
    if is_teacher:
        text = "👨‍🏫 Панель преподавателя"
    
    await callback.message.edit_text(
        text,
        reply_markup=await get_main_menu_keyboard(is_teacher=is_teacher)
    )
    await callback.answer()


@router.callback_query(F.data == "change_group")
async def change_group_start(callback: CallbackQuery, state: FSMContext):
    """Начать смену группы"""
    user_id = callback.from_user.id
    user = await get_user(user_id)
    
    current_group = user.get('user_group') if user else None
    text = "👥 Введите номер вашей группы:"
    if current_group:
        text += f"\n\nТекущая группа: <b>{current_group}</b>"
    
    await callback.message.edit_text(text)
    await state.set_state(GroupState.waiting_for_group)
    await callback.answer()


@router.message(GroupState.waiting_for_group)
async def change_group_process(message: Message, state: FSMContext):
    """Обработка смены группы"""
    user_id = message.from_user.id
    group = message.text.strip()
    
    await update_user_group(user_id, group)
    
    await message.answer(
        f"✅ Группа установлена: <b>{group}</b>",
        reply_markup=await get_main_menu_keyboard(is_teacher=(user_id == TEACHER_ID))
    )
    
    await state.clear()

