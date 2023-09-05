from aiogram import Bot, Dispatcher, types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from config import *
from gsheets_worker import GSheetsWorker as GShW
from datetime import date, timedelta
import itertools


class States(StatesGroup):
    waiting_for_clients_amount = State()
    waiting_for_distances = State()


async def cmd_deliveries(message: types.Message, state: FSMContext):
    await state.finish()
    await send_deliveries(message, state)
    return


async def cmd_delivery_calculation(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer(
        f'Понял, расчитываем доставку. '
        f'Сколько клинтов на пути?'
    )
    await States.waiting_for_clients_amount.set()
    return


async def what_to_do(message: types.Message, state: FSMContext):

    if message.text.lower().startswith('request information:'):
        await state.finish()
        await work_with_tilda(message)
        return

    else:
        pass


async def get_clients_amount(message: types.Message):
    clients_amount = int(message.text.lower())
    if clients_amount == 1:
        await message.answer(
            f'Укажи, через пробел, два расстояния:'
            f'\n-От MakingBaking до клиента'
            f'\n-От клента до дома курьера')
        await States.waiting_for_distances.set()
    elif clients_amount == 2:
        await message.answer(
            f'Укажи, через пробел, три расстояния:'
            f'\n-От MakingBaking до первого клиента'
            f'\n-От первого клинта до второго'
            f'\n-От второго клента до дома курьера')
        await States.waiting_for_distances.set()
    elif clients_amount == 3:
        await message.answer(
            f'Укажи, через пробел, четыре расстояния:'
            f'\n-От MakingBaking до первого клиента'
            f'\n-От первого клинта до второго'
            f'\n-От второго клента до третьего'
            f'\n-От третьего клиента до дома курьера')
        await States.waiting_for_distances.set()
    else:
        await message.answer(
            f'Не умею считать больше трех доставок, '
            f'убедись, что ты ввела число от 1 до 3')
        return


async def delivery_calculation(message: types.Message, state: FSMContext):

    final_price = None
    fix_price_list = [
        i for a in range(300, 751, 50) for i in itertools.repeat(a, 5)
    ]
    fix_distance_list = [i for i in range(1, 51)]
    fix_rate_dict = dict(zip(fix_distance_list, fix_price_list))
    fix_rate_dict.update(dict.fromkeys(range(50, 101), 1200))
    cost_per_kilometer = 7
    distance_from_home_to_mb = 4

    distances = message.text.lower().split(' ')
    if len(distances) == 2:
        distance_from_mb_to_cli = int(distances[0])
        distance_from_cli_to_home = int(distances[1])
        fix_rate = fix_rate_dict[distance_from_mb_to_cli]

        final_price = fix_rate + (
                distance_from_home_to_mb +
                distance_from_mb_to_cli +
                distance_from_cli_to_home
        ) * cost_per_kilometer
    elif len(distances) == 3:
        distance_from_mb_to_cli1 = int(distances[0])
        distance_from_cli1_to_cli2 = int(distances[1])
        distance_from_cli2_to_home = int(distances[2])
        fix_rate_1 = fix_rate_dict[distance_from_mb_to_cli1]
        fix_rate_2 = fix_rate_dict[distance_from_cli1_to_cli2]

        final_price = fix_rate_1 + fix_rate_2 + (
                distance_from_home_to_mb +
                distance_from_mb_to_cli1 +
                distance_from_cli1_to_cli2 +
                distance_from_cli2_to_home
        ) * cost_per_kilometer
    elif len(distances) == 4:
        distance_from_mb_to_cli1 = int(distances[0])
        distance_from_cli1_to_cli2 = int(distances[1])
        distance_from_cli2_to_cli3 = int(distances[2])
        distance_from_cli3_to_home = int(distances[3])
        fix_rate_1 = fix_rate_dict[distance_from_mb_to_cli1]
        fix_rate_2 = fix_rate_dict[distance_from_cli1_to_cli2]
        fix_rate_3 = fix_rate_dict[distance_from_cli2_to_cli3]

        final_price = fix_rate_1 + fix_rate_2 + fix_rate_3 + (
                distance_from_home_to_mb +
                distance_from_mb_to_cli1 +
                distance_from_cli1_to_cli2 +
                distance_from_cli2_to_cli3 +
                distance_from_cli3_to_home
        ) * cost_per_kilometer
    else:
        await message.answer('Что-то пошло не так, пиши создателю')

    await message.answer(f'Стоимость доставки составит {final_price} руб')
    await state.finish()
    return


async def work_with_tilda(message: types.Message):

    tilda_message = message.text.lower()
    worker_id = message.from_user.id

    customer_name = tilda_message[
                    tilda_message.find('name') + 6:tilda_message.find(
                        '2__выберете_удобный')
                    ].title().strip()
    connection = tilda_message[
                 tilda_message.find('для_связи:') + 11:tilda_message.find(
                     'input')
                 ].strip()
    customer_phone = tilda_message[
                     tilda_message.find('input:') + 7:tilda_message.find(
                         '3__дата_заказа')
                     ].replace('+7', '8').strip()
    order_date = tilda_message[
                 tilda_message.find('дата_заказа:') + 13:tilda_message.find(
                     '4__предполагаемое_количество_гостей:')
                 ].replace('-', '.').strip()
    what_cake = tilda_message[
                tilda_message.find('form name:') + 11:tilda_message.find(
                    'https://making-baking.ru/')
                ].strip()
    delivery = tilda_message[
               tilda_message.find('нужна_ли_доставка:') + 19:].strip()
    note = tilda_message[
           tilda_message.find('по_оформлению:') + 15:tilda_message.find(
               'добавить_букет')
           ].strip()
    note = note[:note.find('file_0')].strip()

    if worker_id == 884803519:
        who_work = 'Даша'
    elif worker_id == 295188314:
        who_work = ''
    elif worker_id == 5367841893:
        who_work = ''
    else:
        who_work = 'Аня'

    if delivery.startswith('подойдет'):
        delivery = 'cамовывоз'
    elif delivery.startswith('нужна'):
        delivery = 'доставка от Making.Baking'
    elif delivery.startswith('сам'):
        delivery = 'Яндекс.Доставка'
    elif delivery.startswith('затрудняюсь'):
        delivery = '-'

    if connection == 'telegram':
        communication_method = 'tg ' + customer_phone

    else:
        communication_method = 'wa ' + customer_phone

    card = tilda_message[
           tilda_message.find(
               'открытку_к_заказу:') + 19:].strip()
    if card.startswith('https'):
        card = 'открытка'
    else:
        card = 'нет'

    blank_values = []
    string_data_values = []

    if what_cake == 'бенто-торты':

        what_cake = 'бенто-торт'
        what_taste = tilda_message[
                     tilda_message.find('желаемый_вкус:') + 15:
                     tilda_message.find('7__добавить_ли_свечку')
                     ].strip()
        candle = tilda_message[
                 tilda_message.find('свечку_к_заказу:') + 17:
                 tilda_message.find('8__добавить_ли_вилочки')
                 ].strip()
        fork = tilda_message[
               tilda_message.find('вилочки_к_заказу:') + 18:
               tilda_message.find('9__пожелания_по_оформлению')
               ].strip()
        bouquet = tilda_message[
                  tilda_message.find('букет_к_заказу:') + 16:
                  tilda_message.find('11__нужна_ли_доставка')
                  ].strip()

        extra = ''
        if (candle == 'нет' and fork == 'нет' and
                bouquet == 'нет' and card == 'нет'):
            extra = 'без дополнений'

        if card != 'нет':
            extra = 'открытка '

        if candle != 'нет':
            extra = extra + 'свечка ' + candle[4:] + ' '

        if fork != 'нет':
            extra = extra + 'вилочки ' + fork[4:] + ' '

        if bouquet != 'нет':
            bouquet_price = tilda_message[
                            tilda_message.find(
                                'бюджет_букета_:') + 16:tilda_message.find(
                                '11__нужна_ли_доставка')].strip()
            extra = extra + 'букет на ' + bouquet_price + ' руб'

        blank_values = [
            f'{order_date}', f'{customer_name}', f'{communication_method}',
            f'{what_cake}', f'{what_taste}', f'{extra}', f'{delivery}', '',
            f'{note}', '', '']
        string_data_values = [
            f'{order_date}', f'{customer_name}', f'{communication_method}',
            f'{what_cake}', '', f'{what_taste}', f'{delivery}', '', '',
            f'{card}',
            f'{fork}', f'{candle}', '', '', f'{who_work}']

    elif what_cake == 'бисквитные торты':

        what_cake = 'торт'
        what_taste = tilda_message[
                     tilda_message.find(
                         'тортов_от_15_кг:') + 17:tilda_message.find(
                         '8__пожелания_по_оформлению')].strip()

        if card != 'открытка':
            card = ''

        blank_values = [
            f'{order_date}', f'{customer_name}', f'{communication_method}',
            f'{what_cake}', f'{what_taste}', f'{card}', f'{delivery}', '',
            f'{note}', '', '']
        string_data_values = [
            f'{order_date}', f'{customer_name}', f'{communication_method}',
            f'{what_cake}', '', f'{what_taste}', f'{delivery}', '', '',
            f'{card}', 'нет', 'нет', '', '', f'{who_work}']

    GShW(jsonKeyFileName).insert_data_to_blank(
        blank_spreadsheet_id, blank_values)
    GShW(jsonKeyFileName).insert_string_data_to_blank(
        blank_spreadsheet_id, string_data_values)
    await message.answer(
        f'Добавил клиента с именем {customer_name} в бланк.\n'
        f'Вот ссылка:\n{blank_spreadsheet_link}'
    )

    if delivery == 'доставка от Making.Baking' or delivery == '-':

        recipient_name = tilda_message[
                         tilda_message.find('name_2') + 8:tilda_message.find(
                             'доставка-сюрприз')].title().strip()
        recipient_name = recipient_name[
                         :recipient_name.find(
                             'Phone')].title().strip()
        if len(recipient_name) < 20:
            delivery_date = tilda_message[
                            tilda_message.find(
                                'дата_доставки:') + 15:tilda_message.find(
                                'время_доставки')].replace('-', '.').strip()
            delivery_time = tilda_message[
                            tilda_message.find(
                                'время_доставки:') + 16:tilda_message.find(
                                'name_2')].strip()
            recipient_phone_number = tilda_message[
                                     tilda_message.find(
                                         'phone') + 7:tilda_message.find(
                                         'полный_адрес:')].replace('+7',
                                                                   '8').strip()
            recipient_address = tilda_message[
                                tilda_message.find(
                                    'полный_адрес:') + 14:tilda_message.find(
                                    'additional information')].strip()
            if 'textarea:' in recipient_address:
                delivery_note = recipient_address[recipient_address.find(
                    'textarea:') + 10:].strip()
                recipient_address = recipient_address[:recipient_address.find(
                    'textarea:')].strip()
            else:
                delivery_note = ''
            surprise = tilda_message[tilda_message.find(
                'доставка-сюрприз:') + 18:tilda_message.find('phone')].strip()
            if len(surprise) > 3:
                surprise = 'не указано'

            delivery_values = [
                f'{delivery_date}', f'{delivery_time}', f'{recipient_name}',
                f'{recipient_phone_number}', f'{recipient_address}', '', '',
                '', f'{delivery_note}', f'{what_cake}', f'{surprise}'
            ]
        else:
            delivery_values = [f'Не нужна', f'', f'', f'', f'', f'', f'',
                               f'', f'', f'', f'']

    else:
        delivery_values = [f'Не нужна', f'', f'', f'', f'', f'', f'', f'', f'',
                           f'', f'']

    GShW(jsonKeyFileName).insert_delivery_data_to_blank(
        blank_spreadsheet_id, delivery_values)


async def send_deliveries(message: types.Message, state: FSMContext):

    tommorow_date = (date.today() + timedelta(days=1)).strftime('%d.%m.%Y')
    table_values = GShW(jsonKeyFileName).read_from_delivery_table(
        delivery_spreadsheet_id, delivery_spreadsheet_name, tommorow_date)

    if table_values != 'На завтра доставок нет':

        table_values = table_values.replace(
            "[", ''
        ).replace(
            "]", ''
        ).replace(
            "{", ''
        ).replace(
            "}", ''
        ).replace(
            "'", '^'
        ).replace(
            ", ", ''
        ).replace(
            "]]}]", ''
        ).replace(
            '],', ''
        ).split(f'{tommorow_date}')

        message_data_keys = [
            'time', 'name', 'phone', 'adress', 'door',
            'room', 'floor', 'notice', 'cake', 'surp',
            'pay', 'worker', 'cost'
        ]

        for i in range(len(table_values) - 1):
            message_data_list = str(table_values[i + 1]).replace(
                r'\xa0', ' '
            ).split('^^')
            message_data_dict = dict(
                zip(message_data_keys, message_data_list[1:14])
            )

            await Bot(token=API_TOKEN).send_message(
                -1001693192088,
                f'Дата:  {tommorow_date}\n'
                f'Время:  {message_data_dict["time"]}\n'
                f'Получатель:  {message_data_dict["name"]}\n'
                f'Номер получателя:  {message_data_dict["phone"]}\n'
                f'Адрес, улица:  {message_data_dict["adress"]}\n'
                f'Парадная:  {message_data_dict["door"]}\n'
                f'Квартира:  {message_data_dict["room"]}\n'
                f'Этаж:  {message_data_dict["floor"]}\n'
                f'Примечание:  {message_data_dict["notice"]}\n'
                f'Что:  {message_data_dict["cake"]}\n'
                f'Доставка сюрприз:  {message_data_dict["surp"]}\n'
                f'Остаток с заказчика:  {message_data_dict["pay"]}\n'
                f'Кто везёт:  {message_data_dict["worker"]}\n'
                f'Стоимость:  {message_data_dict["cost"].replace("^", "")}\n'
            )
            await state.finish()
    else:

        await message.answer(
            f'{table_values}'
        )
        await state.finish()


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(
        cmd_deliveries, commands='deliveries', state="*"
    )
    dp.register_message_handler(
        cmd_delivery_calculation, commands='delivery_calculation', state="*"
    )
    dp.register_message_handler(
        get_clients_amount, state=States.waiting_for_clients_amount
    )
    dp.register_message_handler(
        delivery_calculation, state=States.waiting_for_distances
    )
    dp.register_message_handler(
        what_to_do, state="*"
    )
