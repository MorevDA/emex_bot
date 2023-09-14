sorting_options = {'Срок доставки': 'Срок доставки, дней: ', 'Цена, по возрастанию': 'Цена, руб.: '}
sorting_keys = tuple(sorting_options.keys())


def get_analog_or_replacement_parts(parts_dict: dict, sorting_option='Цена, руб.: ') -> list:
    """ Функция для получения информации по аналогам запчасти, как того же производителя, так и других
    производителей(формат данных в обоих случаях идентичен).
    Функция принимает на вход словарь с 'сырыми' данными полученными в результате скрейпинга сайта.
    Функция возвращает словарь с данными приведенными в удобный для пользователя формат.
    По умолчанию выполняется сортировка по цене, опционально возможно менять параметр сортировки при
    вызове функции."""
    analog = []
    for i in parts_dict:
        detail_name = f"<b>{i.get('make')} {i.get('detailNum')} {i.get('name')}</b>\n"
        offers = []
        for j in i.get('offers'):
            part_info: dict = {'Срок доставки, дней: ': j['delivery']['value'], 'Цена, руб.: ':
                               j['displayPrice']['value'], 'Доступно для заказа: ': j['lotQuantity']}
            offers.append(part_info)
        offers.sort(key=lambda x: x[sorting_option])
        analog.append({detail_name: offers[: 3]})
    return analog


def get_analog_or_replacement_parts_string(title: str, parts_dict: dict, sorting_option='Цена, руб.: ') -> str:
    """ Функция для получения информации по аналогам запчасти, как того же производителя, так и других
    производителей(формат данных в обоих случаях идентичен).
    Функция принимает на вход словарь с 'сырыми' данными полученными в результате скрейпинга сайта.
    Функция возвращает словарь с данными приведенными в удобный для пользователя формат.
    По умолчанию выполняется сортировка по цене, опционально возможно менять параметр сортировки при
    вызове функции."""
    analog = f"<b>{title}</b>\n\n"
    for i in parts_dict:
        analog += f"<b>{i.get('make')} {i.get('detailNum')} {i.get('name')}</b>\n"
        offers = []
        for j in i.get('offers'):
            part_info: dict = {'Срок доставки, дней: ': j['delivery']['value'], 'Цена, руб.: ':
                               j['displayPrice']['value'], 'Доступно для заказа': j['lotQuantity']}
            offers.append(part_info)
        offers.sort(key=lambda x: x[sorting_option])
        for offer in offers[: 2]:
            analog += '\n'.join([f'{key} {value}' for key, value in offer.items()]) + '\n\n'
    return analog


def get_original_parts_string(parts_list: dict, sorting_option='Цена, руб.: ') -> str:
    """ Функция для получения информации по запчасти в соответствии с запрошенным номером.
        Функция принимает на вход словарь с 'сырыми' данными полученными в результате скрейпинга сайта.
        Функция возвращает строку с данными приведенными в удобный для пользователя формат, готовую для отправки
        сообщением телеграмм.
        По умолчанию выполняется сортировка по цене, опционально возможно менять параметр сортировки при
        вызове функции."""
    result = '<b>Оригинальные детали по запрошенному номеру:</b>\n'
    detail_name = f"<b>{parts_list[0]['make']} {parts_list[0]['detailNum']} {parts_list[0]['name']}</b>\n"
    result += detail_name
    offers = []
    for part in parts_list[0]['offers']:
        delivery = part['delivery']['value']
        price = part['displayPrice']['value']
        amount = part['quantity']
        part_info = {'Срок доставки, дней: ': delivery, 'Цена, руб.: ': price, 'Доступно для заказа: ': amount}
        offers.append(part_info)
    offers.sort(key=lambda x: x[sorting_option])
    if len(offers) > 0:
        for offer in offers[:5]:
            text = '\n'.join([f'{key} {value}' for key, value in offer.items()]) + '\n\n'
            result += text
    else: result += 'Предложения по оригинальным деталям не найдены'
    return result


def get_info_for_message(input_dict: object, sort_method='Цена, руб.: ') -> list | dict:
    first_strings = ['Аналоги других производителей:', 'Замены того же производителя:']
    match input_dict:
        case {'suggestions': sus}:
            return ['По данному номеру детали нет предложений']
        case {'originals': original, 'analogs': analog, 'replacements': replacement} if len(replacement) > 0 \
                                                                                        and len(analog) > 0:
            return [get_original_parts_string(original, sort_method),
                    get_analog_or_replacement_parts_string(first_strings[1], replacement, sort_method),
                    get_analog_or_replacement_parts_string(first_strings[0], analog, sort_method)]
        case {'originals': original, 'replacements': replacement} if len(replacement) > 0:
            return [get_original_parts_string(original, sort_method),
                    get_analog_or_replacement_parts_string(first_strings[1], replacement, sort_method)]
        case {'originals': original, 'analogs': analog} if len(analog) > 0:
            return [get_original_parts_string(original, sort_method),
                    get_analog_or_replacement_parts_string(first_strings[0], analog, sort_method)]
        case{'originals': original}:
            return [get_original_parts_string(original, sort_method)]
        case _:
            return {i['make']: i['name'] for i in input_dict['makes']['list'] if len(i['name']) > 0}

