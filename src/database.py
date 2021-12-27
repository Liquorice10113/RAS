import sqlite3

class Database():
    def __init__(self) -> None:
        self.conn = sqlite3.connect('test.db')
        c = self.conn.cursor
