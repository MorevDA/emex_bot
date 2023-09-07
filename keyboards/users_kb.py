from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Функция, генерирующая клавиатуру из словаря(для выбора района, филиала, способа сортировки)
def create_inline_keyboard_dict(data:dict) -> InlineKeyboardBuilder:
    """Функция для генерации инлайн клавиатуры из словаря."""
    # Инициализируем билдер
    keyboard: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Добавляем в билдер кнопки
    for key, value in data.items():
        keyboard.row(InlineKeyboardButton(text=key, callback_data=value))
    # Возвращаем объект инлайн-клавиатуры
    return keyboard.as_markup(resize_keyboard=True)


def create_inline_keyboad_in_list(data:list) -> InlineKeyboardBuilder:
    """Функция для генерации инлайн клавиатуры из списка"""
    keyboard: InlineKeyboardBuilder = InlineKeyboardBuilder()
    for elem in data:
        keyboard.row(InlineKeyboardButton(text=elem, callback_data=elem))
    return keyboard.as_markup(resize_keyboard=True)



def create_inline_keyboard_multiple_choice(data: dict) -> InlineKeyboardBuilder:
    """Функция для генерации инлайн клавиатуры для множественного выбора"""
    keyboard: InlineKeyboardBuilder = InlineKeyboardBuilder()
    for name, part in data.items():
        keyboard.row(InlineKeyboardButton(text= f"{name} {part}", callback_data=name))
    return keyboard.as_markup(resize_keyboard=True)
