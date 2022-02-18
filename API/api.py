import sqlite3
import time
from datetime import datetime

from flask import Flask, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abobus'

TG = "telegram"


class IDError(Exception):
    pass


class Database:
    def __init__(self):
        self.con = sqlite3.connect("DataBase/DataBase.db", check_same_thread=False)

    def check_id(self, id):
        cur = self.cur()
        result = cur.execute(
            """SELECT u.id
            FROM users u 
            WHERE u.id == ?""", [id]
        ).fetchone()
        if result:
            return True
        else:
            return False

    def register_id(self, tg_id=None):
        cur = self.cur()
        result = cur.execute(
            """INSERT INTO users(user_tg, user_cnt) 
            VALUES(?, 0)""", [tg_id]
        )
        self.con.commit()
        return result.lastrowid

    def tgid_to_id(self, tgid):
        cur = self.cur()
        result = cur.execute(
            """SELECT u.id
            FROM users u 
            WHERE u.user_tg == ?""", [tgid]
        ).fetchone()
        if result:
            result = result[0]
        return result

    def add_task_to_user(self, id, count):
        cur = self.cur()
        result = cur.execute(
            """UPDATE users
            SET user_cnt = user_cnt + ?
            WHERE id == ?""", [count, id]
        )
        self.con.commit()
        return result

    def add_contest_to_tasks(self, id, count, fin_time):
        current_date = datetime.now().date()
        cur = self.cur()
        result = cur.execute(
            """UPDATE tasks
            SET task_cnt = task_cnt + ?,
            task_time = task_time + ?
            WHERE task_user_id == ? and task_dod == ?""", [count, fin_time, id, current_date]
        )
        self.con.commit()
        if result.rowcount == 1:
            return True
        cur = self.cur()
        result = cur.execute(
            """INSERT INTO tasks(task_user_id, task_cnt, task_dod, task_time) 
            VALUES(?, ?, ?, ?)""", [id, count, current_date, fin_time]
        )
        self.con.commit()
        print(result)
        return True

    def start_new_contest(self, id):
        cur = self.cur()
        cur.execute(
            """INSERT INTO contest(user_id, count, start_time) 
            VALUES(?, 0, ?)""", [id, time.time()]
        )
        self.con.commit()

    def add_task_to_contest(self, id):
        cur = self.cur()
        result = cur.execute(
            """UPDATE contest
            SET count = count + 1
            WHERE user_id == ?""", [id]
        )
        self.con.commit()
        return result

    def del_task_from_contest(self, id):
        cur = self.cur()
        result = cur.execute(
            """UPDATE contest
            SET count = count - 1
            WHERE user_id == ?""", [id]
        )
        self.con.commit()
        return result

    def finish_contest(self, id):
        cur = self.cur()
        result = cur.execute(
            """select start_time, count
            from contest
            where user_id == ?""", [id]
        ).fetchone()
        if not result:
            return None, None
        fin_time = time.time() - result[0]
        count = result[1]

        cur = self.cur()
        result = cur.execute(
            """DELETE from contest
                where user_id == ?""", [id]
        )
        self.con.commit()
        return [int(fin_time), int(count)]

    def get_info_on_date_range(self, id, start, finish):
        cur = self.cur()
        result = cur.execute(
            """select task_cnt, task_time, task_dod
            from tasks
            where task_user_id == ? and
            DATE(task_dod) between DATE(?) and DATE(?)""", [id, start, finish]
        ).fetchall()
        return result

    def get_contest_info(self, id):
        cur = self.cur()
        result = cur.execute(
            """select count, start_time
            from contest
            where user_id == ?""", [id]
        ).fetchone()
        if result:
            fin_time = time.time() - result[1]
            count = result[0]
            return [count, fin_time]
        return None

    def cur(self):
        return self.con.cursor()

    def close(self):
        self.con.close()


@app.route('/start_new_contest/<platform>/<int:id>')
def start_new_contest(platform, id):
    try:
        id = id_processing(id, platform)
    except IDError as e:
        return create_json(False, str(e))
    try:
        DB.start_new_contest(id)
        return create_json(True)
    except sqlite3.IntegrityError:
        return create_json(False, "user exists")


@app.route('/add_task/<platform>/<int:id>')
def add_task(platform, id):
    try:
        id = id_processing(id, platform)
    except IDError as e:
        return create_json(False, str(e))

    res = DB.add_task_to_contest(id)
    if res.rowcount != 1:
        return create_json(False, "contest has not launched")
    return create_json(True)


@app.route('/del_task/<platform>/<int:id>')
def del_task(platform, id):
    try:
        id = id_processing(id, platform)
    except IDError as e:
        return create_json(False, str(e))

    res = DB.del_task_from_contest(id)
    if res.rowcount != 1:
        return create_json(False, "contest has not launched")
    return create_json(True)


@app.route('/finish_contest/<platform>/<int:id>')
def finish_contest(platform, id):
    try:
        id = id_processing(id, platform)
    except IDError as e:
        return create_json(False, str(e))
    fin_time, count = DB.finish_contest(id)
    if fin_time is None:
        return create_json(False, "contest has not started")
    DB.add_contest_to_tasks(id, count, fin_time)
    return create_json(True)


@app.route('/get_day_info/<platform>/<int:id>')
def get_day_info(platform, id=0):
    try:
        id = id_processing(id, platform)
    except IDError as e:
        return create_json(False, str(e))
    cnt = 0
    time = 0
    time_state = False
    res = DB.get_info_on_date_range(id, datetime.now().date(), datetime.now().date())
    if res:
        cnt += res[0][0]
        time += res[0][1]
    res = DB.get_contest_info(id)
    if res:
        time_state = True
        cnt += res[0]
        time += res[1]
    return create_json(True, {
        "task_count": cnt,
        "timer_count": time,
        "timer_state": time_state,
    })


@app.route('/contest_state/<platform>/<int:id>')
def contest_state(platform, id=0):
    try:
        id = id_processing(id, platform)
    except IDError as e:
        return create_json(False, str(e))
    res = DB.get_contest_info(id)
    timer_state = False
    if res:
        timer_state = True
    return create_json(True, timer_state)


@app.route('/get_info/<platform>/<int:id>/<start>/<finish>')
def get_info(platform, id, start, finish):
    try:
        id = id_processing(id, platform)
    except IDError as e:
        return create_json(False, str(e))
    res = DB.get_info_on_date_range(id, start, finish)
    ans = dict()
    if len(res) == 0:
        return create_json(False)
    for date in res:
        ans[date[2]] = {"task_count": date[0], "timer_count": date[1]}
    return create_json(True, ans)


@app.route('/register_id/<platform>/<int:tg_id>')
def register_id(platform, tg_id=0):
    if platform == TG:
        try:
            new_id = DB.register_id(tg_id)
        except sqlite3.IntegrityError:
            return create_json(False, "tg_id already registered")
    else:
        new_id = DB.register_id()
    return create_json(True, str(new_id))


def id_processing(id, platform):
    if platform == TG:
        id = DB.tgid_to_id(id)
        if id is None:
            raise IDError("ID is missing")
    else:
        res = DB.check_id(id)
        if not res:
            raise IDError("ID is missing")
    return id


def create_json(success, data=None):
    json = {
        "success": success,  # True, False
        "data": data,  # ошибка или ответ
    }
    return jsonify(json)


if __name__ == '__main__':
    DB = Database()
    app.run(port=8080, host="127.0.0.1", debug=True)
