import sqlite3
from flask import Flask, jsonify

app = Flask(__name__)
app.config['SECRET_KEY'] = 'abobus'


class Database:
    def __init__(self):
        self.con = sqlite3.connect("DataBase/DataBase.db", check_same_thread=False)

    def get_start_settings(self):
        cur = self.cur()
        result = cur.execute(
            """select * from tasks """
        ).fetchall()
        return result

    def cur(self):
        return self.con.cursor()

    def close(self):
        self.con.close()


@app.route('/')
def hello_world():  # put application's code here

    return jsonify(DB.get_start_settings())


if __name__ == '__main__':
    DB = Database()
    print(DB.get_start_settings())
    app.run(port=8080, host="127.0.0.1", debug=True)
