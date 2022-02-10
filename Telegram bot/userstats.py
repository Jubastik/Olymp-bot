import json
import time
user_stats = {}

def check_user_registration(user):
    return user.id in user_stats


def add_new_user(user):
    user_stats[str(user.id)] = {"task_count": 0, "timer_count": 0, "timer_state": False, "last_time": 0}


def increase_user_task_count(user):
    user_stats[str(user.id)]["task_count"] += 1

def update_timer(user):
    if user_stats[str(user.id)]["timer_state"]:
        user_stats[str(user.id)]["timer_count"] += time.time() - user_stats[str(user.id)]["last_time"]
        user_stats[str(user.id)]["last_time"] = time.time()

def start_timer(user):
    user_stats[str(user.id)]["last_time"] = time.time()

def decrease_user_task_count(user):
    if user_stats[str(user.id)]["task_count"] > 0:
        user_stats[str(user.id)]["task_count"] -= 1
        return True
    else:
        return False


def change_task_state(user):
    user_id = str(user.id)
    user_stats[user_id]["timer_state"] = not user_stats[user_id]["timer_state"]


def set_user_timer_count(user):
    pass


def save():
    serialize_json = json.dumps(user_stats)
    with open(r"files/user_stats.json", "w", encoding="utf-8") as f:
        f.write(serialize_json)


def load():
    with open(r"files/user_stats.json", "r", encoding="utf-8") as f:
        global user_stats
        user_stats = json.loads(f.read())


def get_stat_by_id(user):
    return user_stats[str(user.id)]

