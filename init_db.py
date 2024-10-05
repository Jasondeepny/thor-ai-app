import sqlite3
from contextlib import closing


# 在文件开头添加数据库初始化函数
def init_db():
    with closing(sqlite3.connect("ai_complete.db")) as conn:
        with conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS models (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                )
            """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS roles (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL UNIQUE
                )
            """
            )

            # 插入初始数据
            models = [
                "GPT-4o-2024-08-06",

                "GPT-4o",

                "GPT-4-turbo",

                "Claude-3.5-Sonnet",

                "GPT-4o-mini",

                "GPT-3.5-turbo",

                "GPT-3.5-turbo-instruct",
            ]
                
            roles = [
                "Golang",
                "Python",
                "Java",
                "JavaScript",
                "MySQL",
                "C++",
                "Ruby",
                "PHP",
                "Rust",
                "Swift",
                "Kotlin",
                "TypeScript",
            ]

            conn.executemany(
                "INSERT OR IGNORE INTO models (name) VALUES (?)", [(m,) for m in models]
            )
            conn.executemany(
                "INSERT OR IGNORE INTO roles (name) VALUES (?)", [(r,) for r in roles]
            )

def select_models():
    with closing(sqlite3.connect("ai_complete.db")) as conn:
        with conn:
            return conn.execute("SELECT name FROM models").fetchall()

def select_roles():
    with closing(sqlite3.connect("ai_complete.db")) as conn:
        with conn:
            return conn.execute("SELECT name FROM roles").fetchall()
        

def select_model(name):
    with closing(sqlite3.connect("ai_complete.db")) as conn:
        with conn:
            return conn.execute("SELECT id FROM models WHERE name = ?", (name,)).fetchone()

def select_role(name):
    with closing(sqlite3.connect("ai_complete.db")) as conn:
        with conn:
            return conn.execute("SELECT name FROM roles WHERE name = ?", (name,)).fetchone()

def select_model(name):
    with closing(sqlite3.connect("ai_complete.db")) as conn:
        with conn:
            return conn.execute("SELECT name FROM models WHERE name = ?", (name,)).fetchone()  