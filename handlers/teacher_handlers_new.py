"""
Обработчики для преподавателей
"""
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime, date, time
from functools import wraps

from config import ADMIN_ID
from database.db_sqlserver import (
    get_teacher_schedules, create_request, get_teacher_requests,
    get_user
)
from keyboards.teacher_keyboards import (
    get_teacher_main_keyboard, get_request_type_keyboard,
    get_my_requests_keyboard
)

router = Router()


class RequestState(StatesGroup):
    """Состояния для создания заявки"""
    waiting_for_schedule = State()
    waiting_for_type = State()
    waiting_for_reason = State()
    waiting_for_preferred_times = State()


def check_teacher(func):
    """Декоратор для проверки прав преподавателя"""
    @wraps(func)
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        user = await get_user(callback.from_user.id)
        if not user or user.get('role') != 'teacher':
            await callback.answer("❌ У вас нет прав для выполнения этого действия", show_alert=True)
            return
        return await func(callback, *args, **kwargs)
    return wrapper


@router.callback_query(F.data == "teacher_main")
async def teacher_main_menu(callback: CallbackQuery):
    """Главное меню преподавателя"""
    user = await get_user(callback.from_user.id)
    if not user or user.get('role') != 'teacher':
        await callback.answer("❌ Доступ запрещен", show_alert=True)
        return
    
    text = f"👨‍🏫 <b>Панель преподавателя</b>\n\n"
    text += f"Добро пожаловать, {user.get('teacher_name', 'Преподаватель')}!\n\n"
    text += "Выберите действие:"
    
    await callback.message.edit_text(
        text,
        reply_markup=await get_teacher_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "teacher_my_schedules")
@check_teacher
async def teacher_my_schedules(callback: CallbackQuery):
    """Просмотр своих пар"""
    teacher_id = callback.from_user.id
    schedules = await get_teacher_schedules(teacher_id)
    
    if not schedules:
        text = "❌ У вас пока нет запланированных пар"
    else:
        text = "📚 <b>Ваши пары:</b>\n\n"
        for schedule in schedules:
            text += f"📅 {schedule.get('day_of_week', '')}\n"
            text += f"🕐 {schedule.get('time_start', '')} - {schedule.get('time_end', '')}\n"
            text += f"📖 {schedule.get('subject', '')}\n"
            text += f"🏢 Аудитория: {schedule.get('room', 'Не указана')}\n"
            text += f"👥 Группа: {schedule.get('group_name', 'Не указана')}\n\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=await get_teacher_main_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "teacher_create_request")
@check_teacher
async def teacher_create_request_start(callback: CallbackQuery, state: FSMContext):
    """Начать создание заявки"""
    teacher_id = callback.from_user.id
    schedules = await get_teacher_schedules(teacher_id)
    
    if not schedules:
        await callback.message.edit_text(
            "❌ У вас нет запланированных пар для создания заявки",
            reply_markup=await get_teacher_main_keyboard()
        )
        await callback.answer()
        return
    
    # Показываем список пар для выбора
    text = "📋 <b>Выберите пару для заявки:</b>\n\n"
    keyboard = []
    for schedule in schedules[:10]:  # Ограничиваем 10 парами
        schedule_text = f"{schedule.get('day_of_week')} {schedule.get('time_start')} - {schedule.get('subject')}"
        keyboard.append([{
            "text": schedule_text,
            "callback_data": f"select_schedule_{schedule['id']}"
        }])
    
    # TODO: Реализовать клавиатуру с кнопками
    
    await state.set_state(RequestState.waiting_for_schedule)
    await callback.answer()


@router.callback_query(F.data.startswith("select_schedule_"))
@check_teacher
async def teacher_select_schedule(callback: CallbackQuery, state: FSMContext):
    """Выбор пары для заявки"""
    schedule_id = int(callback.data.replace("select_schedule_", ""))
    await state.update_data(schedule_id=schedule_id)
    
    await callback.message.edit_text(
        "📝 <b>Выберите тип заявки:</b>",
        reply_markup=await get_request_type_keyboard()
    )
    await state.set_state(RequestState.waiting_for_type)
    await callback.answer()


@router.callback_query(F.data.startswith("request_type_"))
@check_teacher
async def teacher_select_request_type(callback: CallbackQuery, state: FSMContext):
    """Выбор типа заявки"""
    request_type = callback.data.replace("request_type_", "")
    await state.update_data(request_type=request_type)
    
    text = "📝 <b>Укажите причину:</b>\n\n"
    text += "Например: болезнь, командировка, конференция и т.д."
    
    await callback.message.edit_text(text)
    await state.set_state(RequestState.waiting_for_reason)
    await callback.answer()


@router.message(RequestState.waiting_for_reason)
async def teacher_enter_reason(message: Message, state: FSMContext):
    """Ввод причины заявки"""
    reason = message.text
    data = await state.get_data()
    request_type = data.get('request_type')
    
    await state.update_data(reason=reason)
    
    if request_type == 'reschedule':
        # Для переноса нужно указать предпочтительные варианты
        text = "📅 <b>Укажите 2-3 предпочтительных варианта переноса:</b>\n\n"
        text += "Формат: ДД.ММ.ГГГГ ЧЧ:ММ-ЧЧ:ММ Аудитория\n"
        text += "Например:\n"
        text += "15.12.2024 10:00-11:30 101\n"
        text += "16.12.2024 14:00-15:30 205"
        
        await message.answer(text)
        await state.set_state(RequestState.waiting_for_preferred_times)
    else:
        # Для отмены или смены аудитории сразу создаем заявку
        await create_teacher_request(message, state)


@router.message(RequestState.waiting_for_preferred_times)
async def teacher_enter_preferred_times(message: Message, state: FSMContext):
    """Ввод предпочтительных вариантов переноса"""
    # Парсим варианты
    lines = message.text.strip().split('\n')
    preferred_times = []
    
    for line in lines[:3]:  # Максимум 3 варианта
        parts = line.split()
        if len(parts) >= 3:
            try:
                date_str = parts[0]
                time_range = parts[1]
                room = parts[2] if len(parts) > 2 else None
                
                # Парсим дату и время
                date_obj = datetime.strptime(date_str, "%d.%m.%Y").date()
                time_start_str, time_end_str = time_range.split('-')
                time_start = datetime.strptime(time_start_str, "%H:%M").time()
                time_end = datetime.strptime(time_end_str, "%H:%M").time()
                
                preferred_times.append({
                    'date': date_obj,
                    'time_start': time_start,
                    'time_end': time_end,
                    'room': room
                })
            except Exception as e:
                await message.answer(f"❌ Ошибка в формате: {line}\nПопробуйте еще раз")
                return
    
    await state.update_data(preferred_times=preferred_times)
    await create_teacher_request(message, state)


async def create_teacher_request(message: Message, state: FSMContext):
    """Создать заявку от преподавателя"""
    data = await state.get_data()
    teacher_id = message.from_user.id
    schedule_id = data.get('schedule_id')
    request_type = data.get('request_type')
    reason = data.get('reason')
    
    try:
        # Подготовка данных для создания заявки
        request_data = {
            'original_date': None,  # TODO: Получить из расписания
            'original_time_start': None,
            'original_time_end': None,
            'original_room': None,
        }
        
        if request_type == 'reschedule':
            preferred_times = data.get('preferred_times', [])
            for i, pref in enumerate(preferred_times[:3], 1):
                request_data[f'preferred_date_{i}'] = pref['date']
                request_data[f'preferred_time_{i}_start'] = pref['time_start']
                request_data[f'preferred_time_{i}_end'] = pref['time_end']
                request_data[f'preferred_room_{i}'] = pref.get('room')
        
        request_id = await create_request(
            teacher_id=teacher_id,
            schedule_id=schedule_id,
            request_type=request_type,
            reason=reason,
            **request_data
        )
        
        await message.answer(
            f"✅ <b>Заявка создана!</b>\n\n"
            f"ID заявки: {request_id}\n"
            f"Статус: На рассмотрении\n\n"
            f"Вы получите уведомление, когда админ рассмотрит заявку.",
            reply_markup=await get_teacher_main_keyboard()
        )
        
    except Exception as e:
        await message.answer(
            f"❌ Ошибка при создании заявки: {str(e)}",
            reply_markup=await get_teacher_main_keyboard()
        )
    
    await state.clear()


@router.callback_query(F.data == "teacher_my_requests")
@check_teacher
async def teacher_my_requests(callback: CallbackQuery):
    """Просмотр своих заявок"""
    teacher_id = callback.from_user.id
    requests = await get_teacher_requests(teacher_id)
    
    if not requests:
        text = "📋 У вас пока нет заявок"
    else:
        text = "📋 <b>Ваши заявки:</b>\n\n"
        for req in requests:
            status_emoji = {
                'pending': '⏳',
                'approved': '✅',
                'rejected': '❌'
            }
            status_text = {
                'pending': 'На рассмотрении',
                'approved': 'Принята',
                'rejected': 'Отклонена'
            }
            
            text += f"{status_emoji.get(req['status'], '❓')} <b>Заявка #{req['id']}</b>\n"
            text += f"Тип: {req.get('request_type', '')}\n"
            text += f"Статус: {status_text.get(req['status'], req['status'])}\n"
            text += f"Дата: {req.get('created_at', '')}\n\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=await get_my_requests_keyboard()
    )
    await callback.answer()

