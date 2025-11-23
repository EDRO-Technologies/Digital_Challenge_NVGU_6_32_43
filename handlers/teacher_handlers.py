from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from functools import wraps
from config import TEACHER_ID
from database.db import (
    add_schedule, get_all_schedules, delete_schedule, get_all_specialties,
    add_specialty, update_schedule, get_schedule_by_id
)
from keyboards.inline import (
    get_main_menu_keyboard, get_teacher_manage_keyboard, get_specialties_keyboard,
    get_confirm_keyboard
)
from utils.formatters import format_schedules_list, format_schedule
from utils.excel_parser import load_all_excel_files

router = Router()


class AddScheduleState(StatesGroup):
    waiting_for_specialty = State()
    waiting_for_day = State()
    waiting_for_time = State()
    waiting_for_subject = State()
    waiting_for_teacher = State()
    waiting_for_room = State()
    waiting_for_group = State()


class EditScheduleState(StatesGroup):
    waiting_for_schedule_id = State()
    waiting_for_field = State()
    waiting_for_value = State()


class AddSpecialtyState(StatesGroup):
    waiting_for_name = State()


from functools import wraps

def check_teacher(func):
    """Декоратор для проверки прав преподавателя"""
    @wraps(func)
    async def wrapper(callback: CallbackQuery, *args, **kwargs):
        if callback.from_user.id != TEACHER_ID:
            await callback.answer("❌ У вас нет прав для выполнения этого действия", show_alert=True)
            return
        return await func(callback, *args, **kwargs)
    return wrapper


@router.callback_query(F.data == "teacher_manage")
@check_teacher
async def teacher_manage(callback: CallbackQuery):
    """Меню управления для преподавателя"""
    await callback.message.edit_text(
        "👨‍🏫 <b>Панель управления</b>\n\n"
        "Выберите действие:",
        reply_markup=await get_teacher_manage_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "choose_specialty")
@check_teacher
async def teacher_choose_specialty(callback: CallbackQuery):
    """Выбор специальности для просмотра расписания (для преподавателя)"""
    keyboard = await get_specialties_keyboard(show_back=True)
    await callback.message.edit_text(
        "📚 Выберите специальность для просмотра расписания:",
        reply_markup=keyboard
    )
    await callback.answer()


@router.callback_query(F.data == "teacher_add")
@check_teacher
async def teacher_add_start(callback: CallbackQuery, state: FSMContext):
    """Начать добавление расписания"""
    keyboard = await get_specialties_keyboard(show_back=True)
    await callback.message.edit_text(
        "➕ <b>Добавление расписания</b>\n\n"
        "Выберите специальность:",
        reply_markup=keyboard
    )
    await state.set_state(AddScheduleState.waiting_for_specialty)
    await callback.answer()


@router.callback_query(AddScheduleState.waiting_for_specialty, F.data.startswith("spec_"))
async def teacher_add_specialty(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора специальности"""
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
    await state.update_data(specialty=specialty_name)
    await callback.message.edit_text(
        f"✅ Специальность: <b>{specialty_name}</b>\n\n"
        "Введите день недели (например: Понедельник):"
    )
    await state.set_state(AddScheduleState.waiting_for_day)
    await callback.answer()


@router.message(AddScheduleState.waiting_for_day)
async def teacher_add_day(message: Message, state: FSMContext):
    """Обработка дня недели"""
    await state.update_data(day=message.text)
    await message.answer("Введите время (например: 09:00-10:30):")
    await state.set_state(AddScheduleState.waiting_for_time)


@router.message(AddScheduleState.waiting_for_time)
async def teacher_add_time(message: Message, state: FSMContext):
    """Обработка времени"""
    await state.update_data(time=message.text)
    await message.answer("Введите название предмета:")
    await state.set_state(AddScheduleState.waiting_for_subject)


@router.message(AddScheduleState.waiting_for_subject)
async def teacher_add_subject(message: Message, state: FSMContext):
    """Обработка предмета"""
    await state.update_data(subject=message.text)
    await message.answer("Введите имя преподавателя (или /skip для пропуска):")
    await state.set_state(AddScheduleState.waiting_for_teacher)


@router.message(AddScheduleState.waiting_for_teacher)
async def teacher_add_teacher(message: Message, state: FSMContext):
    """Обработка преподавателя"""
    if message.text.lower() != '/skip':
        await state.update_data(teacher=message.text)
    await message.answer("Введите номер аудитории (или /skip для пропуска):")
    await state.set_state(AddScheduleState.waiting_for_room)


@router.message(AddScheduleState.waiting_for_room)
async def teacher_add_room(message: Message, state: FSMContext):
    """Обработка аудитории"""
    if message.text.lower() != '/skip':
        await state.update_data(room=message.text)
    await message.answer("Введите номер группы (или /skip для пропуска):")
    await state.set_state(AddScheduleState.waiting_for_group)


@router.message(AddScheduleState.waiting_for_group)
async def teacher_add_group(message: Message, state: FSMContext):
    """Завершение добавления расписания"""
    data = await state.get_data()
    
    if message.text.lower() != '/skip':
        await state.update_data(group=message.text)
        data = await state.get_data()
    
    await add_schedule(
        specialty=data['specialty'],
        day_of_week=data['day'],
        time=data['time'],
        subject=data['subject'],
        teacher=data.get('teacher'),
        room=data.get('room'),
        group_name=data.get('group')
    )
    
    await message.answer(
        "✅ Расписание успешно добавлено!",
        reply_markup=await get_main_menu_keyboard(is_teacher=True)
    )
    
    await state.clear()


@router.callback_query(F.data == "teacher_view_all")
@check_teacher
async def teacher_view_all(callback: CallbackQuery):
    """Просмотр всех расписаний"""
    schedules = await get_all_schedules()
    
    if not schedules:
        text = "❌ Расписания не найдены"
    else:
        text = f"📋 <b>Все расписания</b> (всего: {len(schedules)})\n\n"
        text += format_schedules_list(schedules, "")
    
    # Разбиваем на части, если сообщение слишком длинное
    if len(text) > 4000:
        text = text[:4000] + "\n\n... (сообщение обрезано, используйте поиск)"
    
    await callback.message.edit_text(
        text,
        reply_markup=get_teacher_manage_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "teacher_upload_excel")
@check_teacher
async def teacher_upload_excel(callback: CallbackQuery):
    """Загрузка Excel файлов"""
    await callback.message.edit_text("📤 Загрузка Excel файлов...\n\nЭто может занять некоторое время.")
    await callback.answer()
    
    try:
        import logging
        logger = logging.getLogger(__name__)
        
        logger.info("Начало загрузки Excel файлов")
        total_added = await load_all_excel_files()
        logger.info(f"Загрузка завершена. Добавлено записей: {total_added}")
        
        if total_added > 0:
            await callback.message.edit_text(
                f"✅ Загрузка завершена!\n\n"
                f"Добавлено записей в расписание: <b>{total_added}</b>\n\n"
                f"Файлы успешно обработаны.",
                reply_markup=await get_teacher_manage_keyboard()
            )
        else:
            await callback.message.edit_text(
                f"⚠️ Загрузка завершена, но не было добавлено записей.\n\n"
                f"Проверьте формат файлов в папках '1' и '2'.",
                reply_markup=await get_teacher_manage_keyboard()
            )
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Ошибка при загрузке Excel: {error_details}")
        
        await callback.message.edit_text(
            f"❌ Ошибка при загрузке:\n\n"
            f"<code>{str(e)}</code>\n\n"
            f"Проверьте логи для подробностей.",
            reply_markup=await get_teacher_manage_keyboard()
        )


@router.callback_query(F.data == "teacher_manage_specs")
@check_teacher
async def teacher_manage_specs(callback: CallbackQuery, state: FSMContext):
    """Управление специальностями"""
    specialties = await get_all_specialties()
    
    text = "📚 <b>Управление специальностями</b>\n\n"
    text += "Текущие специальности:\n"
    for spec in specialties:
        text += f"• {spec['name']}\n"
    text += "\nВведите название новой специальности (или /cancel для отмены):"
    
    keyboard = await get_teacher_manage_keyboard()
    await callback.message.edit_text(text, reply_markup=keyboard)
    await state.set_state(AddSpecialtyState.waiting_for_name)
    await callback.answer()


@router.message(AddSpecialtyState.waiting_for_name)
async def teacher_add_specialty_name(message: Message, state: FSMContext):
    """Добавление новой специальности"""
    if message.text.lower() == '/cancel':
        await message.answer(
            "❌ Отменено",
            reply_markup=await get_main_menu_keyboard(is_teacher=True)
        )
        await state.clear()
        return
    
    await add_specialty(message.text)
    await message.answer(
        f"✅ Специальность '{message.text}' добавлена!",
        reply_markup=await get_main_menu_keyboard(is_teacher=True)
    )
    await state.clear()

