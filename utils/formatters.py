def format_schedule(schedule: dict) -> str:
    """Форматирование одной записи расписания"""
    text = f"📚 <b>{schedule['subject']}</b>\n"
    text += f"🕐 {schedule['time']}\n"
    text += f"📅 {schedule['day_of_week']}\n"
    
    if schedule.get('teacher'):
        text += f"👤 Преподаватель: {schedule['teacher']}\n"
    if schedule.get('room'):
        text += f"🏢 Аудитория: {schedule['room']}\n"
    if schedule.get('group_name'):
        text += f"👥 Группа: {schedule['group_name']}\n"
    
    return text


def format_schedules_list(schedules: list, title: str = "Расписание") -> str:
    """Форматирование списка расписаний"""
    if not schedules:
        return f"❌ {title} не найдено"
    
    text = f"📋 <b>{title}</b>\n\n"
    
    current_day = None
    for schedule in schedules:
        day = schedule['day_of_week']
        if day != current_day:
            text += f"\n📅 <b>{day}</b>\n"
            current_day = day
        
        text += f"🕐 {schedule['time']} - {schedule['subject']}"
        if schedule.get('room'):
            text += f" ({schedule['room']})"
        text += "\n"
        
        if schedule.get('teacher'):
            text += f"   👤 {schedule['teacher']}\n"
        if schedule.get('group_name'):
            text += f"   👥 {schedule['group_name']}\n"
        text += "\n"
    
    return text


def format_specialty_list(specialties: list) -> str:
    """Форматирование списка специальностей"""
    if not specialties:
        return "❌ Специальности не найдены"
    
    text = "📚 <b>Доступные специальности:</b>\n\n"
    for spec in specialties:
        text += f"• {spec['name']}\n"
    
    return text

