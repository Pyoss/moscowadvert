import ads
import bot_handlers
import datahandler
import buttons
import config


def new_ad(chat_id, message_id):
    text = 'Итак, начнем!\n'\
            'Создайте своё объявление, после чего отправьте его боту. ' \
            'Опишите выгоды и условия Вашего предложения.\n' \
            'Обязательно укажите своё имя и контакт для связи, номер телефона или телеграмм-логин.\n'
    ads.state_dict[chat_id] = 'text'
    ads.Ad(chat_id=chat_id, message_id=message_id)
    bot_handlers.send_message(chat_id, text)


def add_text(message):
    chat_id = message.from_user.id
    ads.ad_dict[chat_id].edit_text(message)
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
    print(call.data)
    try:
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        if call.data == 'skip':
            skip_photo(call)
        elif call.data == 'public':
            if chat_id in ads.ad_dict:
                ads.ad_dict[chat_id].public(chat_id, call.from_user.first_name)
        elif call.data == 'start_over':
            if chat_id in ads.ad_dict:
                del ads.ad_dict[chat_id]
            if chat_id in ads.state_dict:
                del ads.state_dict[chat_id]
            start_over(call)
        elif call.data.split('_')[0] == 'post':
            ad_id = int(call.data.split('_')[1])
            x = ads.Ad(db_id=ad_id)
            x.public(chat_id, call.from_user.first_name)
        elif call.data.split('_')[0] == 'edit':
            ad_id = int(call.data.split('_')[1])
            ad = ads.Ad(db_id=ad_id)
            ads.ad_dict[chat_id] = ad
            ads.state_dict[chat_id] = 'text'
            ad.author = chat_id
            bot_handlers.send_message(chat_id, 'Отправьте новый текст объявления.')
        elif call.data.split('_')[0] == 'delete':
            ad_id = int(call.data.split('_')[1])
            ad = ads.Ad(db_id=ad_id)
            datahandler.delete_ad(ad)
        bot_handlers.edit_message(chat_id, call.message.message_id, call.message.text)
    except Exception as e:
        message = repr(e)
        bot_handlers.send_message(197216910, message)
        message = call.data
        bot_handlers.send_message(197216910, message)




