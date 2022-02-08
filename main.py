import telebot
from telebot import types

token = "5174930087:AAGoeno-wC93dPb-_z_yCdoHRf_JbqyeZYI"
bot = telebot.TeleBot(token, parse_mode=None)
phrases = ["Ты великолепен!!!", "Под твоей клавиатурой находится меню. Пользуйся!!", "Нажми кнопку Трекер чтобы "
                                                                                     "начать решать задачи. Для "
                                                                                     "получения аналитики нажмите "
                                                                                     "Статистика. Удачи!!!"]


@bot.message_handler(commands=['start'])
def start_message(message):
    # Приветственные сообщения + найстройка меню клавиатуры
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    statistics_button = types.KeyboardButton("Статистика")
    tracker_button = types.KeyboardButton("Трекер")
    markup.row(statistics_button, tracker_button)
    bot.send_message(message.chat.id, phrases[0])
    bot.send_message(message.chat.id, phrases[1])
    bot.send_message(message.chat.id, phrases[2], reply_markup=markup)


@bot.message_handler(content_types='text')
def message_reply(message):
    # Обработка кнопок
    if message.text == "Статистика":
        # Переход в меню статистики
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        return_button = types.KeyboardButton("Назад")
        func1_button = types.KeyboardButton("По кол-ву")
        func2_button = types.KeyboardButton("По времени")
        markup.row(return_button, func1_button, func2_button)
        bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=markup)
    elif message.text == "Назад":
        # Возвращение в корень меню
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        statistics_button = types.KeyboardButton("Статистика")
        tracker_button = types.KeyboardButton("Трекер")
        markup.row(statistics_button, tracker_button)
        bot.send_message(message.chat.id, phrases[2], reply_markup=markup)
    elif message.text == "Трекер":
        # Призыв трекера
        bot.send_message(message.chat.id, "Таймер запущен. \nВы кодите: 15 мин \nРешено: 3 задачи")


bot.polling()
