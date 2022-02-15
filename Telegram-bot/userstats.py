import json
import time
user_stats = {}

def check_user_registration(user):
    # Получает айди пользователя
    return user.id in user_stats
    # Возвращает bool есть ли юзер в системе.


def add_new_user(user):
    #Получает айди пользователя
    user_stats[str(user.id)] = {"task_count": 0, "timer_count": 0, "timer_state": False, "last_time": 0}
    #Регистрация пользователя в системе

def increase_user_task_count(user):
    #Получает айди пользователя
    user_stats[str(user.id)]["task_count"] += 1
    # Устанавливает task_count в значение task_count + 1

def update_timer(user):
    # Получает айди пользователя
    if user_stats[str(user.id)]["timer_state"]:
        user_stats[str(user.id)]["timer_count"] += time.time() - user_stats[str(user.id)]["last_time"]
        user_stats[str(user.id)]["last_time"] = time.time()
    # Обновляет timer_count в бд и возвращает его новое значение
def start_timer(user):
    # Получает айди пользователя и time.time()
    user_stats[str(user.id)]["last_time"] = time.time()
    # Устанавливает в last_time значение time.time()
def decrease_user_task_count(user):
    #Получает айди юзера
    if user_stats[str(user.id)]["task_count"] > 0:
        user_stats[str(user.id)]["task_count"] -= 1
        return True
    else:
        return False
    # Уменьшает task_count Пользователя на 1


def change_timer_state(user):
    # Получает айди юзера
    user_id = str(user.id)
    if not user_stats[user_id]["timer_state"]:
        user_stats[user_id]["last_time"] = time.time()
    user_stats[user_id]["timer_state"] = not user_stats[user_id]["timer_state"]
    # Устанавливает новый timer_state


def set_user_timer_count(user):
    # Получает айди юзера и устанавливаемый timer_count
    pass
    # Устанавливает timer_count пользователя


def save():
     #Не метод api
    serialize_json = json.dumps(user_stats)
    with open(r"files\user_stats.json", "w", encoding="utf-8") as f:
        f.write(serialize_json)


def load():
    # Не метод api
    with open(r"files\user_stats.json", "r", encoding="utf-8") as f:
        global user_stats
        user_stats = json.loads(f.read())

def get_cur_stat_by_id(user):
    #Получает айди пользователя
    pass
    # Возвращает статы по форме {"task_count": 0, "timer_count": 0, "timer_state": False, "last_time": 0} из таблицы со статами текущего дня
def get_stat_by_id(user):
    # Получает айди пользователя а так же список тех параметров, которые нужно вернуть и еще промежуток времени за который нужна статистика
    # (user_id, params = ["task_count","timer_count"], days = 7)
    return user_stats[str(user.id)]
    # возвращает его статы по форме : [ day:{"task_count": 0, "timer_count": 0}, day:{"task_count": 0, "timer_count": 0}, ........... ]

