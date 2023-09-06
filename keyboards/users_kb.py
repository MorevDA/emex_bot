from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


# Функция, генерирующая клавиатуру из словаря(для выбора района, филиала, способа сортировки)
def create_inline_keyboard_dict(data:dict) -> InlineKeyboardBuilder:
    # Инициализируем билдер
    keyboard: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Добавляем в билдер кнопки
    for key, value in data.items():
        keyboard.row(InlineKeyboardButton(text=key, callback_data=value))
    # Возвращаем объект инлайн-клавиатуры
    return keyboard.as_markup(resize_keyboard=True)


# Функция, генерирующая клавиатуру при множественном выборе
def create_inline_keyboard_multiple_choice(data: dict) -> InlineKeyboardBuilder:
    # Инициализируем билдер
    keyboard: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # Добавляем в билдер кнопки
    for name, part in data.items():
        keyboard.row(InlineKeyboardButton(text= f"{name} {part}", callback_data=name))
    # Возвращаем объект инлайн-клавиатуры
    return keyboard.as_markup(resize_keyboard=True)
