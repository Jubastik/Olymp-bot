import sqlite3
import time

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

    def get_start_settings(self):
        cur = self.cur()
        result = cur.execute(
            """select * from tasks """
        ).fetchall()
        return result

    def start_new_contest(self, id):
        cur = self.cur()
        cur.execute(
            """INSERT INTO contest(user_id, count, start_time) 
            VALUES(?, 0, ?)""", [id, time.time()]
        )
        self.con.commit()

    def add_task(self, id):
        cur = self.cur()
        result = cur.execute(
            """UPDATE contest
            SET count = count + 1
            WHERE user_id == ?""", [id]
        )
        self.con.commit()
        return result

    def finish_contest(self, id):
        cur = self.cur()
        result = cur.execute(
            """select start_time 
            from contest
            where user_id == ?""", [id]
        ).fetchone()
        if not result:
            return None
        fin_time = time.time() - result[0]

        cur = self.cur()
        result = cur.execute(
            """DELETE from contest
                where user_id == ?""", [id]
        )
        self.con.commit()
        return int(fin_time)

    def cur(self):
        return self.con.cursor()

    def close(self):
        self.con.close()


@app.route('/')
def hello_world():  # put application's code here
    return jsonify(DB.get_start_settings())


@app.route('/start_new_contest/<platform>/<int:id>')
def start_new_contest(platform, id):
    try:
        id = id_processing(id, platform)
    except IDError as e:
        return str(e)

    try:
        DB.start_new_contest(id)
        return "success"
    except sqlite3.IntegrityError:
        return "user exists"


@app.route('/add_task/<platform>/<int:id>')
def add_task(platform, id):
    try:
        id = id_processing(id, platform)
    except IDError as e:
        return str(e)

    res = DB.add_task(id)
    if res.rowcount != 1:
        return "contest has not launched"
    return "success"


@app.route('/finish_contest/<platform>/<int:id>')
def finish_contest(platform, id):
    try:
        id = id_processing(id, platform)
    except IDError as e:
        return str(e)


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


if __name__ == '__main__':
    DB = Database()
    app.run(port=8080, host="127.0.0.1", debug=True)
