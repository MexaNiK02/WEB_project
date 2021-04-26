# Импортируем нужные модули
from telegram.ext import Updater, MessageHandler, Filters
from telegram.ext import CallbackContext, CommandHandler, ConversationHandler, InlineQueryHandler, CallbackQueryHandler
from telegram import InlineQueryResultArticle, InputTextMessageContent, InlineKeyboardButton
from telegram import ReplyKeyboardMarkup
from telegram import ReplyKeyboardRemove
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from openexchangerate import OpenExchangeRates
import config
import logging
import random
import requests
import json
import geocoder


# Функция help служить для вывода списка команды которые есть у бота
def help(update, context):
    update.message.reply_text("Список команд: \n"
                              "/start - Бот приветствие вас! \n"
                              "/close_keyboard - Сворачивает клавиатурую \n"
                              "/open_keyboard - Разворачиваетю \n"
                              "/stop - Бот прощаетсяю \n"
                              "/random_number <start> <stop> - Генерация рандомного числа в пределах от start до stop. \n"
                              "/mood - Диалог с ботом про настроение с выбором ответаю \n"
                              "/location - Бот попытаеться определить ваше местоположениею \n"
                              "/organization <название> - Поиск ближайщей организации по названиюю \n"
                              "/currency - По этой команде бот сможет вас проконсультировать по курсу популярных валютю \n"
                              "/converter - Бот сконвертирует одну валюту в другую по вашему пожеланиюю \n"
                              "/set_timer <секунды> - Устанавливает таймер, через какое время вернёться ботю \n"
                              "/unset_timer - Если есть действующий таймер то удаляет егою \n"
                              )


# Функция welcome служит для приветствия пользователя
def welcome(update, context):
    reply_keyboard = [['/random_number', '/mood', '/location'],
                      ['/organization', '/currency', '/converter']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text(
        f"Добро пожаловать, {update.message.from_user.first_name}!\n"
        f"Я бот созданный для проекта. \n"
        f"Мой полный список команд вы можете увидеть по команде /help",
        reply_markup=markup
    )


# Функция button служит обработки нажатий на кнопки клавиатуры Inline
def button(update, context):
    query = update.callback_query
    variant = query.data

    if (variant == 'bad') or (variant == 'good'):
        context.user_data['mood'] = variant
        if (variant == 'bad'):
            query.answer()
            query.message.reply_text('Не растраивайся, всё будет хорошо')
        else:
            query.answer()
            query.message.reply_text('Супер! Я рад за тебя')

    if ('currency' in variant):
        context.user_data['currency'] = variant

        url = 'https://currate.ru/api/'
        # currency_list - список валют
        # rates - курс валюты
        geocoder_params = {
            "get": 'rates',
            "key": "b68730ec4630cecb26f978744813a480",
            "pairs": f'{variant[9:]}RUB'
        }

        response = requests.get(url, params=geocoder_params).json()
        print(response)
        course = response['data'][f'{variant[9:]}RUB']

        query.answer()
        query.message.reply_text(f'Курс RUB к {variant[9:]}: {course}')

    # `CallbackQueries` требует ответа, даже если
    # уведомление для пользователя не требуется, в противном
    #  случае у некоторых клиентов могут возникнуть проблемы.
    # смотри https://core.telegram.org/bots/api#callbackquery.
    # query.answer()
    # # редактируем сообщение, тем самым кнопки
    # # в чате заменятся на этот ответ.
    # query.edit_message_text(text=f"Выбранный вариант: {variant}")


# Функция all_messages служит для ответы на сообщение которое не предусмотренно
def all_messages(update, context):
    update.message.reply_text(f'К сожалению я такой команды пока, что нет у меня в списке.\n'
                              f'Но над этим функционалом уже ведёться работа.\n'
                              f'Узнать все мои команды можно команды /help'
                              )


# Функция start участвует в диалоге опроса
def start(update, context):
    update.message.reply_text(
        "Привет. Пройдите небольшой опрос, пожалуйста!\n"
        "Вы можете прервать опрос, послав команду /stop.\n"
        "В каком городе вы живёте?"
    )

    return 1


# Функция stop, по её вызову бот прощаеться
def stop(update, context):
    update.message.reply_text("Жаль. А было бы интересно пообщаться.\n"
                              "Захочешь ещё пообщаться, приходи, буду ждать. Хорошего дня!"
                              )

    return ConversationHandler.END


# Функция first_response участвует в диалоге опроса
def first_response(update, context):
    locality = update.message.text
    update.message.reply_text(
        "Какая погода в городе {locality}?".format(**locals())
    )

    return 2


# Функция second_response участвует в диалоге опроса
def second_response(update, context):
    weather = update.message.text
    print(weather)
    update.message.reply_text("Спасибо за участие в опросе! Всего доброго!"
                              )

    return ConversationHandler.END


# Функция close_keyboard сворачивает клавиатуру
def close_keyboard(update, context):
    update.message.reply_text(
        "Клавиатура свёрнута",
        reply_markup=ReplyKeyboardRemove()
    )


# Функция open_keyboard сворачивает клавиатуру
def open_keyboard(update, context):
    reply_keyboard = [['/random_number', '/mood', '/location'],
                      ['/organization', '/currency', '/converter']]
    markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False)
    update.message.reply_text(
        f"Клавиатура открыта",
        reply_markup=markup
    )


# Функция remove_job_if_exists удаляет задачи из очереди, если они там есть
def remove_job_if_exists(name, context):
    """Удаляем задачу по имени.
    Возвращаем True если задача была успешно удалена."""
    current_jobs = context.job_queue.get_jobs_by_name(name)
    if not current_jobs:
        return False

    for job in current_jobs:
        job.schedule_removal()

    return True


# Функция set_timer устанавливает таймер
def set_timer(update, context):
    """Добавляем задачу в очередь"""
    chat_id = update.message.chat_id

    try:
        # args[0] должен содержать значение аргумента
        # (секунды таймера)
        due = int(context.args[0])
        if due < 0:
            update.message.reply_text(
                'Извините, не умеем возвращаться в прошлое')

            return

        # Добавляем задачу в очередь
        # и останавливаем предыдущую (если она была)
        job_removed = remove_job_if_exists(
            str(chat_id),
            context
        )

        context.job_queue.run_once(
            task,
            due,
            context=chat_id,
            name=str(chat_id)
        )
        text = f'Вернусь через {due} секунд!'
        if job_removed:
            text += ' Старая задача удалена.'
        # Присылаем сообщение о том, что всё получилось.
        update.message.reply_text(text)

    except (IndexError, ValueError):
        update.message.reply_text('Использование: /set_timer <секунд>')


# Функция task запускаеться после окончание таймера, и сообщает о возвращении бота
def task(context):
    """Выводит сообщение"""
    job = context.job
    context.bot.send_message(job.context,
                             text='Вернулся!'
                             )


# Функция unset_timer удаляет все таймеры, и тут же возвращает бота
def unset_timer(update, context):
    chat_id = update.message.chat_id
    job_removed = remove_job_if_exists(str(chat_id), context)
    if job_removed:
        text = 'Хорошо, вернулся сейчас!'
    else:
        text = 'Нет активного таймера.'

    update.message.reply_text(text)


# Функция mood начинает диалог с пользователем про настроение
def mood(update, context):
    button_list = [
        InlineKeyboardButton("Хорошо", callback_data='good'),
        InlineKeyboardButton("Не очень", callback_data='bad')]

    # сборка клавиатуры из кнопок `InlineKeyboardButton`
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
    # отправка клавиатуры в чат
    update.message.reply_text(text="У меня настроение супер, а у тебя?",
                              reply_markup=reply_markup
                              )


# Функция location определяет ваше местоположение
def location(update, context):
    g = geocoder.ip('me')

    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    toponym_lattitude, toponym_longitude = g.latlng

    geocoder_params = {
        "apikey": "40d1649f-0493-4b70-98ba-98533de7710b",
        "geocode": f'{toponym_longitude},{toponym_lattitude}',
        "kind": 'house',
        "format": "json"
    }

    response = requests.get(geocoder_api_server, params=geocoder_params)
    json_response = response.json()
    house = json_response['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['metaDataProperty'][
        'GeocoderMetaData']['text']
    context.user_data['location'] = house
    update.message.reply_text(f'Ваш адресс: {house}')


# Функция inline_caps обработка InLine запросов
def inline_caps(update, context):
    query = update.inline_query.query
    if not query:
        return
    results = list()
    results.append(
        InlineQueryResultArticle(
            id=query.upper(),
            title='Convert to UPPER TEXT',
            input_message_content=InputTextMessageContent(query.upper())
        )
    )
    context.bot.answer_inline_query(update.inline_query.id, results)


# Функция build_menu используеться для расположения кнопок
def build_menu(buttons, n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, [header_buttons])
    if footer_buttons:
        menu.append([footer_buttons])

    return menu


# Функция random_int генерирует случаное число
def random_int(update, context):
    if context.args:
        toponum_to_find = ' '.join(context.args)
        update.message.reply_text(str(random.randint(round(float(toponum_to_find.split()[0])), round(float(toponum_to_find.split()[1])))))
    else:
        update.message.reply_text('Ожидаеться два аругмент')
        update.message.reply_text('/random_number <start> <stop>')


# Функция currency служить для предоставления пользователю курса популярных валют
def currency(update, context):
    button_list = [
        InlineKeyboardButton("USD", callback_data='currency_USD'),
        InlineKeyboardButton("EUR", callback_data='currency_EUR'),
        InlineKeyboardButton("BTC", callback_data='currency_BTC')
    ]

    # сборка клавиатуры из кнопок `InlineKeyboardButton`
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=2))
    # отправка клавиатуры в чат
    update.message.reply_text(text="Выбирите валюту",
                              reply_markup=reply_markup
                              )


# Функция converter_first участвует в конвертации валют
def converter_first(update, context):
    update.message.reply_text(text="Выбирите валюту из которой конвертируем")

    return 1


# Функция converter_second участвует в конвертации валют
def converter_second(update, context):
    context.user_data['convert_out'] = update.message.text
    update.message.reply_text(text="Выбирите валюту в которую конвертируем")

    return 2


# Функция converter_value участвует в конвертации валют
def converter_value(update, context):
    # отправка клавиатуры в чат
    context.user_data['convert_in'] = update.message.text
    update.message.reply_text(text="Введите количество конвертируемой валюты")

    return 3


# Функция converter_end участвует в конвертации валют
def converter_end(update, context):
    # отправка клавиатуры в чат
    context.user_data['convert_value'] = update.message.text
    url = 'https://currate.ru/api/'

    geocoder_params = {
        "get": 'rates', # currency_list - список валют,  rates - курс валюты
        "key": "b68730ec4630cecb26f978744813a480",
        "pairs": f"{context.user_data['convert_out']}{context.user_data['convert_in']}" # только при get = rates
    }
    response = requests.get(url, params=geocoder_params).json()
    if (response['status'] != 200):
        update.message.reply_text(
            f"К сожалению запрос не может быть выполнен, пожалуйста попробуйте снова")

        return ConversationHandler.END

    else:
        course = float(context.user_data['convert_value']) * float(response['data'][f"{context.user_data['convert_out']}{context.user_data['convert_in']}"])
        update.message.reply_text(f"{context.user_data['convert_value']} {context.user_data['convert_out']} = {course} {context.user_data['convert_in']}")

        return ConversationHandler.END


# Функция scale_maps выбирает наиболее удачный масштаб для объекта найденно на карте
def scale_maps(json):
    rect_glas = json["properties"]['ResponseMetaData']["SearchRequest"]["boundedBy"][1]
    toponym = json["features"][0]["geometry"]["coordinates"]
    toponym_longitude, toponym_lattitude = toponym
    print(toponym)

    delta_lattitude = str(abs(float(rect_glas[1]) - float(toponym_lattitude)))
    delta_longitude = delta_lattitude

    return (delta_longitude, delta_lattitude)


# Функция organization находить ближайшую нужную организвацию для пользователя
def organization(update, context):

    # Пусть наше приложение предполагает запуск:
    # python search.py Москва, ул. Ак. Королева, 12
    # Тогда запрос к геокодеру формируется следующим образом:

    geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
    if context.args:
        toponum_to_find = ' '.join(context.args)
        g = geocoder.ip('me')

        geocoder_api_server = "http://geocode-maps.yandex.ru/1.x/"
        toponym_lattitude, toponym_longitude = g.latlng

        search_api_server = "https://search-maps.yandex.ru/v1/"
        api_key = "dda3ddba-c9ea-4ead-9010-f43fbc15c6e3"

        address_ll = f"{toponym_longitude},{toponym_lattitude}"

        search_params = {
            "apikey": api_key,
            "text": toponum_to_find,
            "lang": "ru_RU",
            "ll": address_ll,
            "type": "biz"
        }

        not_response = False
        response = requests.get(search_api_server, params=search_params)
        if not response:
            update.message.reply_text('Ошибка выполнения запроса:')
            update.message.reply_text("Http статус:", response.status_code, "(", response.reason, ")")
            not_response = True

        if not not_response:
            json_response = response.json()

            # Получаем первую найденную организацию.
            organization = json_response["features"][0]
            delta_lon = delta_lat = 0.002
            org_address = organization["properties"]["CompanyMetaData"]["address"]

            # Получаем координаты ответа.
            point = organization["geometry"]["coordinates"]
            org_point = "{0},{1}".format(point[0], point[1])

            # Собираем параметры для запроса к StaticMapsAPI:
            map_params = {
                # позиционируем карту центром на наш исходный адрес
                "l": "map",
                # добавим точку, чтобы указать найденную аптеку
                "pt": f"{org_point},pm2dgl"
            }

            map_api_server = "http://static-maps.yandex.ru/1.x/"
            # ... и выполняем запрос

            static_api_request = f"http://static-maps.yandex.ru/1.x/?pt={org_point},pm2dgl&spn={delta_lon},{delta_lat}&l=map"
            context.bot.send_photo(
                update.message.chat_id,  # Идентификатор чата. Куда посылать картинку.
                # Ссылка на static API, по сути, ссылка на картинку.
                # Телеграму можно передать прямо её, не скачивая предварительно карту.
                static_api_request,
                caption=f'Нашёл: "{toponum_to_find.upper()}", по адресу: {org_address}'
            )
    else:
        update.message.reply_text('Ожидаеться один аругмент')
        update.message.reply_text('/organization <названия>')


# Функция main являеться основной
def main():
    updater = Updater(config.TOKEN, use_context=True)
    dp = updater.dispatcher
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                        level=logging.INFO
                        )

    text_handler = MessageHandler(Filters.text, all_messages)

    conv_handler = ConversationHandler(
        # Точка входа в диалог.
        # В данном случае — команда /start. Она задаёт первый вопрос.
        entry_points=[CommandHandler('converter', converter_first)],

        # Состояние внутри диалога.
        # Вариант с двумя обработчиками, фильтрующими текстовые сообщения.
        states={
            # Функция читает ответ на первый вопрос и задаёт второй.
            1: [MessageHandler(Filters.text, converter_second)],
            # Функция читает ответ на второй вопрос и завершает диалог.
            2: [MessageHandler(Filters.text, converter_value)],
            3: [MessageHandler(Filters.text, converter_end)]
        },

        # Точка прерывания диалога. В данном случае — команда /stop.
        fallbacks=[CommandHandler('stop', stop)])

    # Добавляем в диспетчер обработчики связывая их с функциями
    dp.add_handler(conv_handler)
    dp.add_handler(CommandHandler("random_number", random_int))
    dp.add_handler(CommandHandler("mood", mood))
    dp.add_handler(CommandHandler("stop", stop))
    dp.add_handler(CommandHandler("location", location))
    dp.add_handler(CommandHandler("organization", organization))
    dp.add_handler(CommandHandler("currency", currency))
    dp.add_handler(CommandHandler("close_keyboard", close_keyboard))
    dp.add_handler(CommandHandler("open_keyboard", open_keyboard))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(CommandHandler("start", welcome))
    dp.add_handler(CommandHandler("unset_timer", unset_timer))
    dp.add_handler(CommandHandler("set_timer", set_timer))

    dp.add_handler(CallbackQueryHandler(button, pass_user_data=True))

    dp.add_handler(text_handler)

    updater.start_polling()
    updater.idle()


# Запускаем функцию main если программа была запущенна сама
if __name__ == '__main__':
    main()
