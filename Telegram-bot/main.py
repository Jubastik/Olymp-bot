import time
import logging
from aiogram import Bot, Dispatcher, executor, types
import userstats
import tools

TOKEN = "5174930087:AAGoeno-wC93dPb-_z_yCdoHRf_JbqyeZYI"
phrases = ["Ты великолепен!!!",
           "Под твоей клавиатурой находится меню. Пользуйся!!",
           """Нажми кнопку Трекер чтобы начать решать задачи. Для получения аналитики нажмите Статистика. Удачи!!!"""]
logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN)
dp = Dispatcher(bot)

def start_bot():
    try:
        userstats.load()
        executor.start_polling(dp)
    except Exception as e:
        print(e.with_traceback())
        userstats.save()
    finally:
        userstats.save()


async def spawn_tracker(message: types.Message,edit=False):
    stats = userstats.get_stat_by_id(message.chat)
    msg = "Таймер {}. \nВы кодите: {}\nРешено задач: {}".format(
        "запущен" if stats["timer_state"] else "выключен", tools.new_time_format(time.gmtime(stats["timer_count"])),
        stats["task_count"])
    markup = types.InlineKeyboardMarkup()
    remove_button = types.InlineKeyboardButton("Удалить задачу", callback_data="remove_task")
    add_button = types.InlineKeyboardButton("Добавить задачу", callback_data="add_task")
    change_task_state_button = types.InlineKeyboardButton(
        "Завершить таймер" if stats["timer_state"] else "Запустить таймер",
        callback_data="change_timer_state")
    update_timer_button = types.InlineKeyboardButton("Обновить таймер", callback_data="update_timer")
    markup.row(change_task_state_button)
    markup.row(remove_button, add_button)
    markup.row(update_timer_button)
    if not edit:
        await message.answer(msg,reply_markup=markup)
    else:
        await message.edit_text(msg,reply_markup=markup)


@dp.message_handler(commands=['save'])
def savebot(message):
    bot.send_message(message.chat.id, "Сохраняемся.....")
    userstats.save()


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    # найстройка меню клавиатуры
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    statistics_button = types.KeyboardButton("Статистика")
    tracker_button = types.KeyboardButton("Трекер")
    markup.row(statistics_button, tracker_button)
    # Приветственные сообщения
    await message.answer(phrases[0])
    time.sleep(1)
    await message.answer(phrases[1])
    time.sleep(1)
    await message.answer(phrases[2], reply_markup=markup)
    # Регистрация нового пользователя
    if not userstats.check_user_registration(message.from_user):
        userstats.add_new_user(message.from_user)


@dp.message_handler(content_types='text')
async def message_reply(message: types.Message):
    # Обработка кнопок
    if message.text == "Статистика":
        # Переход в меню статистики
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        return_button = types.KeyboardButton("Назад")
        func1_button = types.KeyboardButton("По кол-ву")
        func2_button = types.KeyboardButton("По времени")
        markup.row(return_button, func1_button, func2_button)
        await message.answer('Выберите что вам надо', reply_markup=markup)
    elif message.text == "Назад":
        # Возвращение в корень меню
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        statistics_button = types.KeyboardButton("Статистика")
        tracker_button = types.KeyboardButton("Трекер")
        markup.row(statistics_button, tracker_button)
        await message.answer(phrases[2], reply_markup=markup)
    elif message.text == "Трекер":
        # Призыв трекера
        userstats.update_timer(message.from_user)
        await spawn_tracker(message=message,edit=False)


@dp.callback_query_handler(lambda m: True)
async def query_handler(call):
    if call.message:
        stats = userstats.get_stat_by_id(call.message.chat)
        # Функция удаления задач
        if call.data == "remove_task":
            # Проверка что задач не ноль, чтобы телеграм не ругался
            if userstats.decrease_user_task_count(call.message.chat):
                await spawn_tracker(message=call.message, edit=True)

        # Изменение состояния таймера
        elif call.data == "change_timer_state":
            userstats.update_timer(call.message.chat)
            userstats.change_timer_state(call.message.chat)
            await spawn_tracker(message=call.message, edit=True)
        # Обновление таймера
        elif call.data == "update_timer":
            if stats["timer_state"]:
                time.sleep(1)
                userstats.update_timer(call.message.chat)
                await spawn_tracker(message=call.message, edit=True)
        # Функция добавления задачи
        elif call.data == "add_task":
            userstats.increase_user_task_count(call.message.chat)
            await spawn_tracker(message=call.message, edit=True)


if __name__ == "__main__":
    start_bot()
