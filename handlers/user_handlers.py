from aiogram import Router
from aiogram.filters import Command, StateFilter, Text
from aiogram.types import CallbackQuery, Message
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.fsm.storage.memory import MemoryStorage

from keyboards.users_kb import (create_inline_keyboard_dict, create_inline_keyboard_multiple_choice,
                                create_inline_keyboard_in_list)
from lexicon.lexicon import LEXICON
from lexicon.filials import points, points_id
from database.database import users_db
from service.pars_emex import sorting_options
from service.scrap_emex import (get_search_result, base_search_url, alter_search_url, headers_search, params_search,
                                alter_params_search)
from service.pars_emex import get_info_for_message

# Инициализируем хранилище (создаем экземпляр класса MemoryStorage)
storage: MemoryStorage = MemoryStorage()

# Инициализируем роутер
router: Router = Router()

dev = 'Аналоги других производителей'


# Создаем класс, наследуемый от StatesGroup, для группы состояний нашей FSM
class FSMFilial(StatesGroup):
    fill_area = State()  # Состояние ожидания выбора района
    fill_filial = State()  # Состояние ожидания выбора филиала


#     fill_analog = State()  # Состояние ожидания использовать ли аналоги при поиске


# Этот хэндлер будет срабатывать на команду "/start" -
# отправлять ему приветственное сообщение и инлайн клавиатуру
# для выбора района
@router.message(Command(commands='start'))
async def process_start_command(message: Message):
    if message.from_user.id not in users_db:
        await message.answer(text=LEXICON['/start'])
    else:
        await message.answer(text=LEXICON['old_user'])


# Этот хэндлер будет срабатывать на команду "/select_pick_point" - отправлять сообщение
# о необходимости выбора района и инлайн клавиатуру для выбора района
@router.message(Command(commands='select_pick_point'), StateFilter(default_state))
async def process_select_pick_points(message: Message, state: FSMContext):
    await message.answer(text=LEXICON[message.text],
                         reply_markup=create_inline_keyboard_in_list(points.keys()))
    await state.set_state(FSMFilial.fill_area)


# Этот хэндлер будет срабатывать на результат выбора района и
# переводить бота в состояние ожидания выбора пункта
@router.callback_query(StateFilter(FSMFilial.fill_area), Text(text=list(points.keys())))
async def process_point_choice(callback: CallbackQuery, state: FSMContext):
    # Сохраняем данные о выбранном районе по ключу "area"
    await state.update_data(area=callback.data)
    user_id = callback.from_user.id
    district = callback.data
    print(district)
    users_db[user_id] = {'district': district}
    await callback.message.edit_text(text=LEXICON['pickup_point'],
                                     reply_markup=create_inline_keyboard_dict(points[district]))
    await state.set_state(FSMFilial.fill_filial)


# Этот хэндлер будет срабатывать, если во время выбора района будет введено что-то некорректное
@router.message(StateFilter(FSMFilial.fill_area))
async def warning_not_area(message: Message):
    await message.answer(text= LEXICON['select_district'],
                                     reply_markup=create_inline_keyboard_in_list(points.keys()))


# Этот хэндлер будет срабатывать на результат выбора района и
# переводить бота в состояние ожидания выбора пункта выдачи
@router.callback_query(StateFilter(FSMFilial.fill_filial), Text(text=points_id))
async def process_point_choice(callback: CallbackQuery, state: FSMContext):
    await state.update_data(pick_point=callback.data) # Сохраняем данные о точке выдачи по ключу "pick_point"
    users_db[callback.from_user.id] = await state.get_data() # добавляем в базу данных информацию о данных выбранных
    # пользователем  район и пункт выдачи
    await state.clear() # Завершаем машину состояний
    await callback.message.edit_text(text= LEXICON['select_point_complete'],
                                     reply_markup=create_inline_keyboard_dict(sorting_options))


# Этот хэндлер будет срабатывать, если во время выбора пункта выдачи будет введено что-то некорректное
@router.message(StateFilter(FSMFilial.fill_filial))
async def warning_not_area(message: Message):
    user_district = users_db[message.from_user.id]['district']
    await message.answer(text= LEXICON['select_pick_point'],
                                     reply_markup=create_inline_keyboard_dict(points[user_district]))


# Этот хэндлер срабатывает на отправку команды изменения параметров сортировки
# и отправляет инлайн клавиатуру с вариантами сортировки
@router.message(Command('change_sort_param'))
async def change_sort_param(message: Message):
    if message.from_user.id in users_db:
        await message.answer(text=LEXICON['/change_sort_param'],
                             reply_markup=create_inline_keyboard_dict(sorting_options))
    else:
        await message.answer(text=LEXICON['not_in_db'])

# Хэндлер для комманды повторить поиск. Параметры для поискового запроса извлекаются из базы данных
@router.message(Command(commands='repeat_search'))
async def repeat_search(message: Message):
    user_id = message.from_user.id
    if user_id in users_db and 'part' in users_db[user_id]:
        params_search['searchString'] = users_db[user_id]['part']
        params_search['locationId'] = users_db[user_id]['pick_point']
        result = get_search_result(base_search_url, headers_search, params_search)
        sort_params = users_db[user_id]['sort_method']
        search_result = get_info_for_message(result, sort_params)
        if isinstance(search_result, list):
            for message_string in search_result:
                await message.answer(text=message_string)
        else:
            await message.answer(text=LEXICON['multiple_choice'],
                                 reply_markup=create_inline_keyboard_multiple_choice(search_result))
    elif user_id in users_db:
        await message.answer(text = LEXICON.get('first_search'))
    else:
        await message.answer(text=LEXICON['not_in_db'])


# Хэндлер будет срабатывать на выбор способа сортировки и вносить данные о выборе пользователя
# в базу данных
@router.callback_query(Text(text=sorting_options.values()))
async def select_sort_options(callback: CallbackQuery):
    user_id = callback.from_user.id
    if 'sort_method' in users_db[user_id]:
        sort_options = callback.data
        users_db[user_id]['sort_method'] = sort_options
        await callback.message.edit_text(text=LEXICON['change_sort_param'])
    else:
        sort_options = callback.data
        users_db[user_id]['sort_method'] = sort_options
        await callback.message.edit_text(text=LEXICON['start search'])


# Хэндлер для обработки простых текстовых сообщений от пользователя. Если пользователь внесен в базу данных
# (завершен FSM) будет запущен поиск по тексту переданному в сообщении.
@router.message(Text)
async def start_search(message: Message):
    if message.from_user.id not in users_db:
        await message.answer(text=LEXICON['not_in_db'])
    else:
        users_db[message.from_user.id]['part'] = message.text
        params_search['searchString'] = message.text
        params_search['locationId'] = users_db[message.from_user.id]['pick_point']
        result = get_search_result(base_search_url, headers_search, params_search)
        sort_params = users_db[message.from_user.id]['sort_method']
        search_result = get_info_for_message(result, sort_params)
        if isinstance(search_result, list):
            for message_string in search_result:
                await message.answer(text=message_string)
        else:
            await message.answer(text=LEXICON['multiple_choice'],
                                 reply_markup=create_inline_keyboard_multiple_choice(search_result))


@router.callback_query(Text)
async def start_alter_search(callback: CallbackQuery):
    user_id = callback.from_user.id
    try:
        alter_params_search['make'] = callback.data.lower()
        alter_params_search['detailNum'] = users_db[user_id]['part']
        alter_params_search['locationId'] = users_db[user_id]['pick_point']
        alter_result: object = get_search_result(alter_search_url, headers_search, alter_params_search)
        sort_params = users_db[user_id]['sort_method']
        res_search = get_info_for_message(alter_result, sort_params)
        await callback.answer(
            text="Идет поиск информации, это может занять некоторое время.",
            show_alert=True)
        for msg in res_search:
            await callback.message.answer(text=msg)
    except:
        await callback.message.answer(text=LEXICON['not_in_db'])
