from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from keyboards.inline import get_main_menu_keyboard
from config import TEACHER_ID

router = Router()


@router.message()
async def handle_unknown_message(message: Message, state: FSMContext):
    """Обработка неизвестных сообщений (не команд)"""
    # Пропускаем команды
    if message.text and message.text.startswith('/'):
        return
    
    # Пропускаем сообщения, которые обрабатываются FSM состояниями
    current_state = await state.get_state()
    if current_state is not None:
        return
    
    user_id = message.from_user.id
    is_teacher = user_id == TEACHER_ID
    
    await message.answer(
        "🤔 К сожалению, я не знаю такой команды...\n\n"
        "Используйте кнопки меню для навигации.",
        reply_markup=await get_main_menu_keyboard(is_teacher=is_teacher)
    )


@router.callback_query()
async def handle_unknown_callback(callback: CallbackQuery):
    """Обработка неизвестных callback запросов"""
    user_id = callback.from_user.id
    is_teacher = user_id == TEACHER_ID
    
    await callback.answer(
        "🤔 К сожалению, я не знаю такой команды...",
        show_alert=True
    )
    
    await callback.message.edit_text(
        "🤔 К сожалению, я не знаю такой команды...\n\n"
        "Используйте кнопки меню для навигации.",
        reply_markup=await get_main_menu_keyboard(is_teacher=is_teacher)
    )
