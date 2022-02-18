import time
import logging
from aiogram import Bot, Dispatcher, executor, types
import api_interface as api
import tools
from config import TOKEN, PHRASES,PATH_TO_PHOTOS
import os

logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN)
dp = Dispatcher(bot)


def start_bot():
    executor.start_polling(dp)


async def spawn_tracker(message: types.Message, edit=False):
    stats = api.get_day_stat_by_id(message.chat.id)
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
        await message.answer(msg, reply_markup=markup)
    else:
        await message.edit_text(msg, reply_markup=markup)


@dp.message_handler(commands=['save'])
async def savebot(message: types.Message):
    await message.answer(message.chat.id, "Сохраняемся.....")


@dp.message_handler(commands=['start'])
async def start_message(message: types.Message):
    # найстройка меню клавиатуры
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    statistics_button = types.KeyboardButton("Статистика")
    tracker_button = types.KeyboardButton("Трекер")
    markup.row(statistics_button, tracker_button)

    # Регистрация пользователя
    api.add_new_user(message.from_user.id)

    # Приветственные сообщения
    await message.answer(PHRASES[0])
    time.sleep(1)
    await message.answer(PHRASES[1])
    time.sleep(1)
    await message.answer(PHRASES[2], reply_markup=markup)
    # Регистрация нового пользователя


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
        await message.answer(PHRASES[2], reply_markup=markup)
    elif message.text == "Трекер":
        # Призыв трекера
        await spawn_tracker(message=message, edit=False)
    elif message.text == "По кол-ву":
        if tools.create_plot(plot_type="task", period=1, count=1, user_id=message.chat.id):
            photo = open("files/photos/{}.png".format(message.chat.id), "rb")
            await message.answer_photo(photo)
            photo.close()
            os.remove(PATH_TO_PHOTOS + "{}.png".format(message.chat.id))
        else:
            await message.answer("Что-то пошло не так, пожалуйста, попробуйте снова!")
    elif message.text == "По времени":
        if tools.create_plot(plot_type="time", period=1, count=1, user_id=message.chat.id):
            photo = open(PATH_TO_PHOTOS+"{}.png".format(message.chat.id), "rb")
            await message.answer_photo(photo)
            photo.close()
            os.remove("files/photos/{}.png".format(message.chat.id))
        else:
            await message.answer("Что-то пошло не так, пожалуйста, попробуйте снова!")


@dp.callback_query_handler(lambda m: True)
async def query_handler(call):
    if call.message:
        stats = api.get_day_stat_by_id(call.message.chat.id)
        # Функция удаления задач
        if call.data == "remove_task":
            # Проверка что задач не ноль, чтобы телеграм не ругался
            if api.decrease_user_task_count(call.message.chat.id):
                await spawn_tracker(message=call.message, edit=True)

        # Изменение состояния таймера
        elif call.data == "change_timer_state":
            api.change_timer_state(call.message.chat.id)
            await spawn_tracker(message=call.message, edit=True)
        # Обновление таймера
        elif call.data == "update_timer":
            if stats["timer_state"]:
                time.sleep(1)
                await spawn_tracker(message=call.message, edit=True)
        # Функция добавления задачи
        elif call.data == "add_task":
            api.increase_user_task_count(call.message.chat.id)
            await spawn_tracker(message=call.message, edit=True)


if __name__ == "__main__":
    start_bot()
