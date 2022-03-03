import json
import time
from config import SERVER_PATH
import requests
from datetime import datetime, timedelta

user_stats = {}


def check_user_registration(user):
    # Получает айди пользователя
    return user.id in user_stats
    # Возвращает bool есть ли юзер в системе.


def add_new_user(user_id):
    # Получает айди пользователя
    query = "register_id/telegram/{}".format(user_id)
    res = requests.get(SERVER_PATH + query)
    return res
    # Регистрация пользователя в системе


def increase_user_task_count(user_id):
    # Получает айди пользователя
    query = "add_task/telegram/{}".format(user_id)
    res = requests.get(SERVER_PATH + query)
    return res
    # Устанавливает task_count в значение task_count + 1


def update_timer(user):
    # Получает айди пользователя
    if user_stats[str(user.id)]["timer_state"]:
        user_stats[str(user.id)]["timer_count"] += time.time() - user_stats[str(user.id)]["last_time"]
        user_stats[str(user.id)]["last_time"] = time.time()
    # Обновляет timer_count в бд и возвращает его новое значение


def start_timer(user_id):
    # Получает айди пользователя и time.time()
    query = "start_new_contest/telegram/{}".format(user_id)
    res = requests.get(SERVER_PATH + query)
    return res
    # Устанавливает в last_time значение time.time()


def stop_timer(user_id):
    query = "finish_contest/telegram/{}".format(user_id)
    res = requests.get(SERVER_PATH + query)
    print(res.text)
    return res


def get_timer_state(user_id):
    query = "contest_state/telegram/{}".format(user_id)
    res = requests.get(SERVER_PATH + query)
    return json.loads(res.text)["data"]

def get_user_main_stat(user_id):
    query = "/telegram/{}".format(user_id)
    res = requests.get(SERVER_PATH + query)
    return json.loads(res.text)["data"]

def decrease_user_task_count(user_id):
    # Получает айди юзера
    query = "del_task/telegram/{}".format(user_id)
    res = requests.get(SERVER_PATH + query)
    return res
    # Уменьшает task_count Пользователя на 1


def change_timer_state(user_id):
    # Получает айди юзера
    timer_state = get_timer_state(user_id)
    if timer_state:
        stop_timer(user_id)
    else:
        start_timer(user_id)
    return True
    # Устанавливает новый timer_state


def set_user_timer_count(user):
    # Получает айди юзера и устанавливаемый timer_count
    pass
    # Устанавливает timer_count пользователя


def save():
    # Не метод api
    serialize_json = json.dumps(user_stats)
    with open(r"files\user_stats.json", "w", encoding="utf-8") as f:
        f.write(serialize_json)


def load():
    # Не метод api
    with open(r"files\user_stats.json", "r", encoding="utf-8") as f:
        global user_stats
        user_stats = json.loads(f.read())


def get_day_stat_by_id(user_id):
    # Получает айди пользователя
    query = "get_day_info/telegram/{}".format(user_id)
    res = requests.get(SERVER_PATH + query)
    res = json.loads(res.text)
    return res["data"]
    # Возвращает статы по форме {"task_count": 0, "timer_count": 0, "timer_state": False, "last_time": 0} из таблицы со статами текущего дня
    #{"date" : { "task_count" : 0, "timer_count":0}, ... "date" : {"task_count" : 0, "timer_count":0}}

def get_stat_by_id(user_id, days):
    end = datetime.now().date()
    start = end - timedelta(days=days)
    query = "get_info/telegram/{}/{}/{}".format(user_id, start, end)
    res = requests.get(SERVER_PATH + query)
    print(res.text)
    res = json.loads(res.text)
    return res["data"]
