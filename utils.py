import ads
import bot_handlers
import datahandler
import buttons
import config


def new_ad(chat_id, message_id):
    text = 'Итак, начнем!\n'\
           'Сначала укажите свои контактные данные для связи (телеграмм-логин или номер телефона/Whatsapp)' \
           ' и отправьте их боту.'
    ads.state_dict[chat_id] = 'contact'
    ads.Ad(chat_id=chat_id, message_id=message_id)
    bot_handlers.send_message(chat_id, text)


def add_contacts(message):
    chat_id = message.from_user.id
    ads.ad_dict[chat_id].contacts = message.text
    ads.state_dict[chat_id] = 'text'
    text = 'Отлично!\n'\
           'Теперь создайте текст объявления, опишите выгоды и условия Вашего предложения.\n'
            'Если Вы являетесь АН или агентом, обязательно укажите размер Вашей комиссии.'
    ads.ad_dict[chat_id].skip_message = bot_handlers.send_message(
        message.from_user.id, text)


def add_text(message):
    chat_id = message.from_user.id
    ads.ad_dict[chat_id].edit_text(message.text)
    ads.ad_dict[chat_id].add_contacts()
    ads.state_dict[chat_id] = 'photo'
    text = 'Хорошо!\n'\
           'Теперь отправьте боту одно или несколько фото(альбом) для объявления.' \
           'Фото выгодно выделит Ваше объявления среди других.\n' \
           '(или пропустите этот шаг)'
    ads.ad_dict[chat_id].skip_message = bot_handlers.send_message(
        message.from_user.id, text, reply_markup=buttons.skip_keyboard())


def add_photo(message):
    chat_id = message.from_user.id
    if chat_id == config.admin_id:
        ads.ad_dict[chat_id].album = []
    photo = message.photo[0].file_id
    ads.ad_dict[chat_id].edit_album(photo)
    ads.state_dict[chat_id] = 'photo_new'
    bot_handlers.edit_message(chat_id=chat_id, message_id=ads.ad_dict[chat_id].skip_message.message_id,
                              text=ads.ad_dict[chat_id].skip_message.text)

    text = 'Замечательно! '\
           'Объявление готово.\n' \
           'Публикуем?'
    bot_handlers.send_message(message.from_user.id, text, reply_markup=buttons.public_keyboard())


def skip_photo(call):

    text = 'Замечательно! '\
           'Объявление готово.\n' \
           'Публикуем?'
    bot_handlers.send_message(call.from_user.id, text, reply_markup=buttons.public_keyboard())


def ask_question(chat_id, username):
    if username is None:
        bot_handlers.send_message(chat_id, 'Чтобы иметь возможность задать'
                                           ' вопрос необходимо создать юзернейм в телеграмме.')

    text = 'Напишите Ваш вопрос (несколько вопросов) и отправьте его боту. Вам ответят в личку.'
    ads.state_dict[chat_id] = 'question'
    bot_handlers.send_message(chat_id, text)


def contacts(chat_id):
    text = 'Прямая связь с админом канала: \n@YaZanoza.\nПросьба беспокоить только в крайнем случае! ' \
           'Вопросы задавайте через пункт меню "Задать вопрос".'
    bot_handlers.send_message(chat_id, text)


def start_over(call):
    bot_handlers.send_message(call.from_user.id, '{}, необходимо выбрать новый пункт меню!'.format(call.from_user.first_name))


def call_handler(call):
    message = call.data
    bot_handlers.send_message(197216910, message)
    try:
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        if call.data == 'skip':
            bot_handlers.delete_message(chat_id, message_id)
            skip_photo(call)
        elif call.data == 'public':
            if chat_id in ads.ad_dict:
                bot_handlers.delete_message(chat_id, message_id)
                ads.ad_dict[chat_id].public(chat_id, call.from_user.first_name)
        elif call.data == 'start_over':
            if chat_id in ads.ad_dict:
                del ads.ad_dict[chat_id]
            if chat_id in ads.state_dict:
                del ads.state_dict[chat_id]
            bot_handlers.delete_message(chat_id, message_id)
            start_over(call)
        elif call.data.split('_')[0] == 'post':
            ad_id = int(call.data.split('_')[1])
            ad = ads.Ad(db_id=ad_id)
            ad.public(chat_id, call.from_user.first_name)
            bot_handlers.delete_message(chat_id, message_id)
            for i in range(0, len(ad.album)):
                bot_handlers.delete_message(chat_id, message_id-(i+1))
        elif call.data.split('_')[0] == 'edit':
            ad_id = int(call.data.split('_')[1])
            ad = ads.Ad(db_id=ad_id)
            ads.ad_dict[chat_id] = ad
            ads.state_dict[chat_id] = 'text'
            ad.author = chat_id
            bot_handlers.delete_message(chat_id, message_id)
            bot_handlers.send_message(chat_id, 'Отправьте новый текст объявления.')
        elif call.data.split('_')[0] == 'delete':
            bot_handlers.delete_message(chat_id, message_id)
            ad_id = int(call.data.split('_')[1])
            ad = ads.Ad(db_id=ad_id)
            try:
                datahandler.delete_ad(ad)
                for i in range(0, len(ad.album)):
                    bot_handlers.delete_message(chat_id, message_id-(i+1))
            except:
                pass
    except Exception as e:
        if str(e) == """A request to the Telegram API was unsuccessful. The server returned HTTP 400 Bad Request. Response body:
[b'{"ok":false,"error_code":400,"description":"Bad Request: too much messages to send as an album"}']""":
            bot_handlers.bot.answer_callback_query(call.id, 'Изображений слишком много. Пожалуйста, оформите '
                                                            'объявление с меньшим количеством изображений.', show_alert=True)
        chat_id = call.message.chat.id
        if chat_id in ads.ad_dict:
            del ads.ad_dict[chat_id]
        if chat_id in ads.state_dict:
            del ads.state_dict[chat_id]
        start_over(call)
        message = repr(e)
        bot_handlers.send_message(197216910, message)



