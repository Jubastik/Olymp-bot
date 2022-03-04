import time
import logging
from aiogram import Bot, Dispatcher, executor, types
import api_interface as api
import tools
from config import TOKEN, PHRASES, PATH_TO_PHOTOS
import os
import datetime

logging.basicConfig(level=logging.INFO)
bot = Bot(TOKEN)
dp = Dispatcher(bot)


def start_bot():
    executor.start_polling(dp)


def day_solving(user_id):
    stats = api.get_stat_by_id(user_id, 1000)
    date = (datetime.datetime.now()).date()
    cnt = 0
    if not (str(date) not in stats or stats[str(date)]["task_count"] < 1):
        cnt += 1
    date -= datetime.timedelta(days=1)
    for i in range(1000):
        if str(date) not in stats or stats[str(date)]["task_count"] < 1:
            break
        else:
            cnt += 1
        date -= datetime.timedelta(days=1)
    return cnt


async def spawn_user_main_stat(message: types.Message):
    stats = api.get_user_main_stat(message.chat.id)
    msg = ""
    msg += "😀Это ваша статистика😀\n\n"
    msg += "🎓Общее число решенных задач: 🎓{} \n\n".format(stats["count"] )
    msg += "⏳Общее время решения: {} ⏳\n\n".format(tools.new_time_format(time.gmtime(stats["time"])))
    msg += "Вы решаете уже {} days подряд!\nТак держать👍\n Продолжайте в том же духе😆\n🤩И вы станете настоящим dungeon master!🤩\n".format(day_solving(message.chat.id))
    markup = types.InlineKeyboardMarkup()
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_from_main_stat")
    markup.add(back_button)
    await message.edit_text(msg, reply_markup=markup)


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
async def menu_controller(message: types.Message):
    if message.text == "Статистика":
        markup = types.InlineKeyboardMarkup()
        plots_button = types.InlineKeyboardButton("📈Графики📈", callback_data="plots")
        main_stat_button = types.InlineKeyboardButton("📋Общая статистика📋", callback_data="main_stat")
        markup.add(plots_button, main_stat_button)
        await message.answer(
            "📋Здесь статистика📋\n"
            "💎Выбирай то, что тебе нужно💎",
            reply_markup=markup)
    elif message.text == "Трекер":
        # Призыв трекера
        await spawn_tracker(message=message, edit=False)


@dp.message_handler(commands=['save'])
async def savebot(message: types.Message):
    await message.answer(message.chat.id, "Сохраняемся.....")


@dp.callback_query_handler(lambda m: True)
async def query_handler(call: types.CallbackQuery):
    if call.message:
        stats = api.get_day_stat_by_id(call.message.chat.id)
        # Функция удаления задач
        if call.data == "remove_task":
            if api.decrease_user_task_count(call.message.chat.id):
                await spawn_tracker(message=call.message, edit=True)
            else:
                await call.answer(
                    "Удалять задачи можно только со включенным таймером. Так же стоит убедиться, что у вас решено не ноль задач!!!",
                    show_alert=True)

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
            if api.increase_user_task_count(call.message.chat.id):
                await spawn_tracker(message=call.message, edit=True)
            else:
                await call.answer("Добавлять задачи можно только со включенным таймером!!!", show_alert=True)
        elif call.data == "plots":
            markup = types.InlineKeyboardMarkup()
            back_button = types.InlineKeyboardButton("Назад", callback_data="back_from_plots")
            task_plot_button = types.InlineKeyboardButton("По кол-ву", callback_data="make_task_plot")
            time_plot_button = types.InlineKeyboardButton("По времени", callback_data="make_time_plot")
            markup.add(back_button, task_plot_button, time_plot_button)
            await call.message.edit_text(
                "Вы перешли в сервис построения графиков, выберите какой тип графика вам нужен", reply_markup=markup)
        elif call.data == "back_from_plots":
            markup = types.InlineKeyboardMarkup()
            plots_button = types.InlineKeyboardButton("📈Графики📈", callback_data="plots")
            main_stat_button = types.InlineKeyboardButton("📋Общая статистика📋", callback_data="main_stat")
            markup.add(plots_button, main_stat_button)
            await call.message.edit_text(
                "📋Здесь статистика📋\n"
                "💎Выбирай то, что тебе нужно💎",
                reply_markup=markup)
        elif call.data == "main_stat":
            markup = types.InlineKeyboardMarkup()
            back_from_main_stat_button = types.InlineKeyboardButton("Назад", callback_data="back_from_main_stat")
            markup.add(back_from_main_stat_button)
            await spawn_user_main_stat(call.message)
        elif call.data == "back_from_main_stat":
            markup = types.InlineKeyboardMarkup()
            plots_button = types.InlineKeyboardButton("📈Графики📈", callback_data="plots")
            main_stat_button = types.InlineKeyboardButton("📋Общая статистика📋", callback_data="main_stat")
            markup.add(plots_button, main_stat_button)
            await call.message.edit_text(
                "📋Здесь статистика📋\n"
                "💎Выбирай то, что тебе нужно💎",
                reply_markup=markup)
        elif call.data == "make_task_plot":
            markup = types.InlineKeyboardMarkup()
            back_button = types.InlineKeyboardButton("Назад", callback_data="back_from_task_plot")
            week_button = types.InlineKeyboardButton("1 неделя", callback_data="make_one_week_task_plot")
            two_week_button = types.InlineKeyboardButton("2 недели", callback_data="make_two_week_task_plot")
            month_button = types.InlineKeyboardButton("1 месяц", callback_data="make_one_month_task_plot")
            three_month_button = types.InlineKeyboardButton("3 месяца", callback_data="make_three_month_task_plot")
            six_month_button = types.InlineKeyboardButton("6 месяцев", callback_data="make_six_month_task_plot")
            year_button = types.InlineKeyboardButton("1 год", callback_data="make_one_year_task_plot")
            markup.row(back_button)
            markup.row(week_button, two_week_button)
            markup.row(month_button, three_month_button)
            markup.row(six_month_button, year_button)
            await call.message.edit_text("Вы находитесь в меню построения графиков по количеству решенных вами задач, "
                                         "здесь вы можете выбирать промежуток времени, по которому будет строиться "
                                         "график", reply_markup=markup)
        elif call.data == "make_time_plot":
            markup = types.InlineKeyboardMarkup()
            back_button = types.InlineKeyboardButton("Назад", callback_data="back_from_time_plot")
            week_button = types.InlineKeyboardButton("1 неделя", callback_data="make_one_week_time_plot")
            two_week_button = types.InlineKeyboardButton("2 недели", callback_data="make_two_week_time_plot")
            month_button = types.InlineKeyboardButton("1 месяц", callback_data="make_one_month_time_plot")
            three_month_button = types.InlineKeyboardButton("3 месяца", callback_data="make_three_month_time_plot")
            six_month_button = types.InlineKeyboardButton("6 месяцев", callback_data="make_six_month_time_plot")
            year_button = types.InlineKeyboardButton("1 год", callback_data="make_one_year_time_plot")
            markup.row(back_button)
            markup.row(week_button, two_week_button)
            markup.row(month_button, three_month_button)
            markup.row(six_month_button, year_button)
            await call.message.edit_text(
                "Вы находитесь в меню построения графиков по времени, потраченным вами на решение задач, "
                "здесь вы можете выбирать промежуток времени, по которому будет строиться "
                "график", reply_markup=markup)
        elif call.data == "back_from_task_plot" or call.data == "back_from_time_plot":
            markup = types.InlineKeyboardMarkup()
            back_button = types.InlineKeyboardButton("Назад", callback_data="back_from_plots")
            task_plot_button = types.InlineKeyboardButton("По кол-ву", callback_data="make_task_plot")
            time_plot_button = types.InlineKeyboardButton("По времени", callback_data="make_time_plot")
            markup.add(back_button, task_plot_button, time_plot_button)
            await call.message.edit_text(
                "Вы перешли в сервис построения графиков, выберите какой тип графика вам нужен", reply_markup=markup)
        elif call.data == "make_one_week_task_plot":
            if tools.create_plot(plot_type="task", period=1, count=7, user_id=call.message.chat.id):
                photo = open(PATH_TO_PHOTOS + "{}.png".format(call.message.chat.id), "rb")
                msg = call.message
                await call.message.delete()
                await msg.copy_to(call.message.chat.id)
                photo.close()
                os.remove(PATH_TO_PHOTOS + "{}.png".format(call.message.chat.id))
            else:
                await call.message.answer("Извините, что-то пошло не так попробуйте снова!")
        elif call.data == "make_one_week_time_plot":
            if tools.create_plot(plot_type="time", period=1, count=7, user_id=call.message.chat.id):
                photo = open(PATH_TO_PHOTOS + "{}.png".format(call.message.chat.id), "rb")
                await call.message.answer_photo(photo)
                photo.close()
                os.remove(PATH_TO_PHOTOS + "{}.png".format(call.message.chat.id))
            else:
                await call.message.answer("Извините, что-то пошло не так попробуйте снова!")
        elif call.data == "make_two_week_task_plot":
            if tools.create_plot(plot_type="task", period=1, count=14, user_id=call.message.chat.id):
                photo = open(PATH_TO_PHOTOS + "{}.png".format(call.message.chat.id), "rb")
                await call.message.answer_photo(photo)
                photo.close()
                os.remove(PATH_TO_PHOTOS + "{}.png".format(call.message.chat.id))
            else:
                await call.message.answer("Извините, что-то пошло не так попробуйте снова!")
        elif call.data == "make_two_week_time_plot":
            if tools.create_plot(plot_type="time", period=1, count=14, user_id=call.message.chat.id):
                photo = open(PATH_TO_PHOTOS + "{}.png".format(call.message.chat.id), "rb")
                await call.message.answer_photo(photo)
                photo.close()
                os.remove(PATH_TO_PHOTOS + "{}.png".format(call.message.chat.id))
            else:
                await call.message.answer("Извините, что-то пошло не так, попробуйте снова!")
        elif call.data == "make_one_month_task_plot":
            if tools.create_plot(plot_type="task", period=7, count=5, user_id=call.message.chat.id):
                photo = open(PATH_TO_PHOTOS + "{}.png".format(call.message.chat.id), "rb")
                await call.message.answer_photo(photo)
                photo.close()
                os.remove(PATH_TO_PHOTOS + "{}.png".format(call.message.chat.id))
            else:
                await call.message.answer("Извините, что-то пошло не так, попробуйте снова!")
        elif call.data == "make_one_moth_time_plot":
            if tools.create_plot(plot_type="task", period=7, count=5, user_id=call.message.chat.id):
                photo = open(PATH_TO_PHOTOS + "{}.png".format(call.message.chat.id), "rb")
                await call.message.answer_photo(photo)
                photo.close()
                os.remove(PATH_TO_PHOTOS + "{}.png".format(call.message.chat.id))
            else:
                await call.message.answer("Извините, что-то пошло не так попробуйте снова!")
        elif call.data == "make_three_month_task_plot":
            if tools.create_plot(plot_type="task", period=7, count=5, user_id=call.message.chat.id):
                photo = open(PATH_TO_PHOTOS + "{}.png".format(call.message.chat.id), "rb")
                await call.message.answer_photo(photo)
                photo.close()
                os.remove(PATH_TO_PHOTOS + "{}.png".format(call.message.chat.id))
            else:
                await call.message.answer("Извините, что-то пошло не так попробуйте снова!")
        elif call.data == "make_three_moth_time_plot":
            if tools.create_plot(plot_type="task", period=7, count=5, user_id=call.message.chat.id):
                photo = open(PATH_TO_PHOTOS + "{}.png".format(call.message.chat.id), "rb")
                await call.message.answer_photo(photo)
                photo.close()
                os.remove(PATH_TO_PHOTOS + "{}.png".format(call.message.chat.id))
            else:
                await call.message.answer("Извините, что-то пошло не так попробуйте снова!")
        elif call.data == "make_six_month_task_plot":
            if tools.create_plot(plot_type="task", period=7, count=5, user_id=call.message.chat.id):
                photo = open(PATH_TO_PHOTOS + "{}.png".format(call.message.chat.id), "rb")
                await call.message.answer_photo(photo)
                photo.close()
                os.remove(PATH_TO_PHOTOS + "{}.png".format(call.message.chat.id))
            else:
                await call.message.answer("Извините, что-то пошло не так попробуйте снова!")
        elif call.data == "make_six_moth_time_plot":
            if tools.create_plot(plot_type="task", period=7, count=5, user_id=call.message.chat.id):
                photo = open(PATH_TO_PHOTOS + "{}.png".format(call.message.chat.id), "rb")
                await call.message.answer_photo(photo)
                photo.close()
                os.remove(PATH_TO_PHOTOS + "{}.png".format(call.message.chat.id))
            else:
                await call.message.answer("Извините, что-то пошло не так попробуйте снова!")
        elif call.data == "make_one_year_task_plot":
            if tools.create_plot(plot_type="task", period=7, count=5, user_id=call.message.chat.id):
                photo = open(PATH_TO_PHOTOS + "{}.png".format(call.message.chat.id), "rb")
                await call.message.answer_photo(photo)
                photo.close()
                os.remove(PATH_TO_PHOTOS + "{}.png".format(call.message.chat.id))
            else:
                await call.message.answer("Извините, что-то пошло не так попробуйте снова!")
        elif call.data == "make_one_year_time_plot":
            if tools.create_plot(plot_type="task", period=7, count=5, user_id=call.message.chat.id):
                photo = open(PATH_TO_PHOTOS + "{}.png".format(call.message.chat.id), "rb")
                await call.message.answer_photo(photo)
                photo.close()
                os.remove(PATH_TO_PHOTOS + "{}.png".format(call.message.chat.id))
            else:
                await call.message.answer("Извините, что-то пошло не так попробуйте снова!")


if __name__ == "__main__":
    start_bot()
