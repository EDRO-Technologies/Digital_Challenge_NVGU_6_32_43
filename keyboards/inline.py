from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.db import get_all_specialties


async def get_specialties_keyboard(show_back: bool = True):
    """Клавиатура для выбора специальности"""
    specialties = await get_all_specialties()
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    # Группируем кнопки по 2 в ряд
    row = []
    for spec in specialties:
        # Используем ID вместо названия, чтобы избежать превышения лимита callback_data (64 байта)
        spec_id = spec.get('id')
        if spec_id is None:
            # Если нет ID, используем хеш названия как fallback
            import hashlib
            spec_id = int(hashlib.md5(spec['name'].encode('utf-8')).hexdigest()[:8], 16)
        
        # Ограничиваем длину текста кнопки для лучшего отображения
        button_text = spec['name']
        if len(button_text) > 30:
            button_text = button_text[:27] + "..."
        
        row.append(InlineKeyboardButton(
            text=button_text,
            callback_data=f"spec_{spec_id}"
        ))
        if len(row) == 2:
            keyboard.inline_keyboard.append(row)
            row = []
    if row:
        keyboard.inline_keyboard.append(row)
    
    # Добавляем кнопку "Назад"
    if show_back:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
        ])
    
    return keyboard


def get_days_keyboard():
    """Клавиатура для выбора дня недели"""
    days = [
        ("Понедельник", "day_Понедельник"),
        ("Вторник", "day_Вторник"),
        ("Среда", "day_Среда"),
        ("Четверг", "day_Четверг"),
        ("Пятница", "day_Пятница"),
        ("Суббота", "day_Суббота"),
        ("Воскресенье", "day_Воскресенье"),
        ("Вся неделя", "day_all")
    ]
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    row = []
    for day_name, callback_data in days:
        row.append(InlineKeyboardButton(text=day_name, callback_data=callback_data))
        if len(row) == 2:
            keyboard.inline_keyboard.append(row)
            row = []
    if row:
        keyboard.inline_keyboard.append(row)
    
    # Добавляем кнопку "Назад"
    keyboard.inline_keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")
    ])
    
    return keyboard


async def get_main_menu_keyboard(is_teacher: bool = False):
    """Главное меню"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    
    if is_teacher:
        # Меню для преподавателя
        keyboard.inline_keyboard = [
            [InlineKeyboardButton(text="➕ Добавить расписание", callback_data="teacher_add")],
            [InlineKeyboardButton(text="📝 Управление", callback_data="teacher_manage")]
        ]
    else:
        # Меню для студентов
        keyboard.inline_keyboard = [
            [InlineKeyboardButton(text="📚 Выбрать специальность", callback_data="choose_specialty")],
            [InlineKeyboardButton(text="📅 Расписание на сегодня", callback_data="today_schedule")],
            [InlineKeyboardButton(text="📋 Расписание на неделю", callback_data="week_schedule")],
            [InlineKeyboardButton(text="🔍 Поиск", callback_data="search_schedule")],
            [InlineKeyboardButton(text="👥 Изменить группу", callback_data="change_group")]
        ]
    
    return keyboard


async def get_teacher_manage_keyboard():
    """Клавиатура управления для преподавателя"""
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📚 Просмотр расписания", callback_data="choose_specialty")],
        [InlineKeyboardButton(text="📋 Все расписания", callback_data="teacher_view_all")],
        [InlineKeyboardButton(text="📤 Загрузить Excel", callback_data="teacher_upload_excel")],
        [InlineKeyboardButton(text="📚 Управление специальностями", callback_data="teacher_manage_specs")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="main_menu")]
    ])


def get_confirm_keyboard(action: str, item_id: int = None):
    """Клавиатура подтверждения"""
    callback_data = f"confirm_{action}"
    if item_id:
        callback_data += f"_{item_id}"
    
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да", callback_data=callback_data),
            InlineKeyboardButton(text="❌ Нет", callback_data="cancel")
        ]
    ])

