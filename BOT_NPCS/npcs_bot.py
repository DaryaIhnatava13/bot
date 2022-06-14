# импортируем установленную библиотеку https://pypi.org/project/pyTelegramBotAPI/
import telebot
# импортируем бузу данных
import sqlite3
# импортируем спец.объект для создания кнопок
from telebot import types
# модуль pathlib для манипуляции путями файловых систем независимо от операционной системы
from pathlib import Path
# Открываем файл для чтения и считываем из него строку токена
with open('npcs_bot_token.txt', 'r', encoding='utf-8') as file:
    token = file.readline()
# Инициализируем бот
bot = telebot.TeleBot(token)
# переменная для имени пользователя
name = ''
# обработка сообщений (commands(команды),chat_types(private or supergroup),content_types(photo,text,video,document и т.д.),
# regexp(текстовые сообщения, которые подходят под регулярное выражение),func).
@bot.message_handler(commands=['start'])
# функция принимает один параметр (сообщение от пользователя)
def start(message):
    # бот отвечает на сообщение пользователя
    bot.reply_to(message, 'Добрый день! Как к Вам можно обращаться?')
    # зарегистрируем имя пользователя, чтобы проверить правильность
    bot.register_next_step_handler(message, reg_name)
# проверим внесенное пользователем имя с помощью кнопок
def reg_name(message):
    global name
    name = message.text
    # переменная для создания кнопок, встроенных в сообщение
    markup = types.InlineKeyboardMarkup()
    # назначение названия для кнопки
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='Yes')
    # добавление кнопки
    markup.add(key_yes)
    # назначение переменной для кнопки
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='No')
    markup.add(key_no)
    question = 'Вас зовут ' + name + '?'
    # reply_markup прикрепляет кнопку
    bot.send_message(message.from_user.id, text=question, reply_markup=markup)
# после выбора варианта (нажатия кнопки) пользователем дальнейшие действия
@bot.callback_query_handler(func=lambda call: call.data=='Yes')
def callback_worker(call):
    bot.send_message(call.message.chat.id, text='Приятно познакомиться, ' + name + '! Запишу Вас в нашу БД')
    bot.send_message(call.message.chat.id, text='Для выбора интересующей Вас услуги введите слово <u>zakaz</u>', parse_mode='html')
# после выбора варианта (нажатия кнопки) пользователем дальнейшие действия бота
@bot.callback_query_handler(func=lambda call: call.data=='No')
def callback_worker(call):
    bot.send_message(call.message.chat.id, text='Попробуем снова')
    bot.send_message(call.message.chat.id, text='Добрый день! Как к Вам можно обращаться?')
    bot.register_next_step_handler(call.message, reg_name)
# создание кнопок на панели.
@bot.message_handler(func = lambda message: message.text == 'zakaz')
def vybor(message):
    zakaz = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1, one_time_keyboard=True)
    # назначение переменных для кнопок
    proekt = types.KeyboardButton(text='Проектирование')
    avtorskij = types.KeyboardButton(text='Авторский надзор')
    konsult = types.KeyboardButton(text='Консультация')
    zakaz.add(proekt, avtorskij, konsult)
    bot.send_message(message.chat.id, text='Выберите, пожалуйста, услугу!', reply_markup=zakaz)
@bot.message_handler(content_types=['text'])
def bot_message(message):
    proekt = 'Проектирование'
    avtorskij = 'Авторский надзор'
    konsult = 'Консультация'
    if message.text == 'Проектирование':
        bot.send_message(message.chat.id, 'Вы выбрали ' + proekt + '. ' + 'Пришлите документ(архив) с информацией об объекте')
    elif message.text == 'Авторский надзор':
        bot.send_message(message.chat.id, 'Вы выбрали ' + avtorskij + '. ' + 'Пришлите документ(архив) с информацией о строящемся объекте')
    elif message.text == 'Консультация':
        bot.send_message(message.chat.id, 'Вы выбрали ' + konsult + '. ' + 'Пришлите документ(архив) с описанием вашего вопроса')
@bot.message_handler(content_types=['document', 'photo'])
def handler_file(message):
    Path(f'files/{message.chat.id}/{message.chat.username}/').mkdir(parents=True, exist_ok=True)
    if message.content_type == 'photo':
        # создаем переменные и сохраняем фото
        file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = f'files/{message.chat.id}/{message.chat.username}/' + file_info.file_path.replace('photos/', '')
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.reply_to(message, "Мы сохраним ваше фото")
    elif message.content_type == 'document':
        # создаем переменные и сохраняем документ
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        src = f'files/{message.chat.id}/{message.chat.username}/' + message.document.file_name
        with open(src, 'wb') as new_file:
            new_file.write(downloaded_file)
        bot.reply_to(message, "Мы сохраним ваш файл")
    bot.send_message(message.chat.id, 'Напишите, ваш телефон или E-mail, чтобы обсудить дальнейший план работы')
    # запишем данные от пользователя
    bot.register_next_step_handler(message, tel_email)
@bot.message_handler(content_types=['text'])
def tel_email(message):
    tel = message.text
    # Создаём Базу данных. NPCS.db – имя БД,
    conn = sqlite3.connect('NPCS.db')
    # Создаем объект cursor, который позволяет нам взаимодействовать с базой данных и добавлять записи
    cursor = conn.cursor()
    # Создадим таблицу с 4 колонками
    cursor.execute(
        '''CREATE TABLE IF NOT EXISTS NPCS(id INTEGER PRIMARY KEY AUTOINCREMENT, 
        chat_id TEXT, username TEXT, phone TEXT, name TEXT)''')
    # Заполняем таблицу данными
    cursor.execute('''INSERT INTO NPCS(chat_id, username, phone, name) 
    VALUES(?, ?, ?, ?)''', (message.chat.id, message.chat.username, tel, name))
    # Сохраняем изменения
    conn.commit()
    bot.reply_to(message, "Спасибо. Наш менеджер с вами свяжется!")
    site = types.InlineKeyboardMarkup()
    site.add(types.InlineKeyboardButton('Посетить веб-сайт', url='http://ooonpcs.com'))
    bot.send_message(message.chat.id, 'А сейчас можете посетить наш веб-сайт', reply_markup=site)
    bot.send_message(message.chat.id, 'Благодарим за выбор нашей организации!')
# запускаем бот на постоянную обработку
bot.polling(none_stop=True, interval=0)