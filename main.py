import telebot
from telebot import types
import userstats
import time

TOKEN = "5174930087:AAGoeno-wC93dPb-_z_yCdoHRf_JbqyeZYI"
bot = telebot.TeleBot(TOKEN, parse_mode=None)
phrases = ["Ты великолепен!!!", "Под твоей клавиатурой находится меню. Пользуйся!!", "Нажми кнопку Трекер чтобы "
                                                                                     "начать решать задачи. Для "
                                                                                     "получения аналитики нажмите "
                                                                                     "Статистика. Удачи!!!"]


def spawn_tracker(stats, call=None, message=None):
    msg = "Таймер {}. \nВы кодите: {}\nРешено задач: {}".format(
        "запущен" if stats["timer_state"] else "выключен", time.strftime("%H:%M:%S", time.gmtime(stats["timer_count"])), stats["task_count"])
    markup = types.InlineKeyboardMarkup()
    remove_button = types.InlineKeyboardButton("Удалить задачу", callback_data="remove_task")
    change_task_state_button = types.InlineKeyboardButton(
        "Закончить решать задачу" if stats["timer_state"] else "Начать решать задачу",
        callback_data="change_timer_state")
    update_timer_button = types.InlineKeyboardButton("Обновить таймер", callback_data="update_timer")
    markup.row(remove_button, change_task_state_button)
    markup.row(update_timer_button)
    if call is None:
        bot.send_message(message.chat.id, msg, reply_markup=markup)
    elif message is None:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id, text=msg,
                              reply_markup=markup)


@bot.message_handler(commands=['save'])
def savebot(message):
    bot.send_message(message.chat.id, "Сохраняемся.....")
    userstats.save()


@bot.message_handler(commands=['start'])
def start_message(message):
    # найстройка меню клавиатуры
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    statistics_button = types.KeyboardButton("Статистика")
    tracker_button = types.KeyboardButton("Трекер")
    markup.row(statistics_button, tracker_button)
    # Приветственные сообщения
    bot.send_message(message.chat.id, phrases[0])
    time.sleep(1)
    bot.send_message(message.chat.id, phrases[1])
    time.sleep(1)
    bot.send_message(message.chat.id, phrases[2], reply_markup=markup)
    # Регистрация нового пользователя
    if not userstats.check_user_registration(message.from_user):
        userstats.add_new_user(message.from_user)


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
        stats = userstats.get_stat_by_id(message.from_user)
        userstats.update_timer(message.from_user)
        spawn_tracker(stats, message=message)


@bot.callback_query_handler(lambda m: True)
def query_handler(call):
    if call.message:
        # Функция удаления задач
        if call.data == "remove_task":
            # Проверка что задач не ноль, чтобы телеграм не ругался
            if userstats.decrease_user_task_count(call.message.chat):
                stats = userstats.get_stat_by_id(call.message.chat)
                spawn_tracker(stats, call)

        # Изменение состояния таймера + трекинг задач
        elif call.data == "change_timer_state":
            stats = userstats.get_stat_by_id(call.message.chat)
            if stats["timer_state"]:
                userstats.increase_user_task_count(call.message.chat)
                userstats.update_timer(call.message.chat)
            else:
                userstats.start_timer(call.message.chat)
            userstats.change_task_state(call.message.chat)
            spawn_tracker(stats, call=call)
        elif call.data == "update_timer":
            stats = userstats.get_stat_by_id(call.message.chat)
            if stats["timer_state"]:
                userstats.update_timer(call.message.chat)
                spawn_tracker(stats, call=call)


try:
    userstats.load()
    bot.polling()
except ZeroDivisionError:
    userstats.save()
finally:
    userstats.save()
