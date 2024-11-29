import sqlite3
from typing import Any, Dict, List


def with_db(func):
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect("target.db")
        cursor = conn.cursor()
        try:
            result = func(cursor, *args, **kwargs)
            conn.commit()
            return result
        finally:
            conn.close()

    return wrapper


@with_db
def init(cursor):
    """
    디비 테이블 초기화
    """
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS coin (
            id INTEGER PRIMARY KEY autoincrement,
            coin_name TEXT UNIQUE,
            ticker_name TEXT UNIQUE,
            is_active INTEGER DEFAULT 1,
            description TEXT,
            category TEXT,
            rank INTEGER
        );
        """
    )


@with_db
def get_all_targets(cursor) -> List[Dict[str, Any]]:
    """
    모든 코인 조회
    """
    cursor.execute(
        "SELECT * FROM coin WHERE rank IS NOT NULL AND category IS NOT NULL ORDER BY rank ASC;"
    )
    rows = cursor.fetchall()
    return list(
        map(
            lambda x: {
                "id": x[0],
                "coin_name": x[1],
                "ticker_name": x[2],
                "is_active": x[3] == 1,
                "description": x[4],
            },
            rows,
        )
    )


@with_db
def get_active_targets(cursor) -> List[str]:
    """
    활성화된 코인 조회
    """
    cursor.execute(
        "SELECT ticker_name FROM coin WHERE is_active = 1 ORDER BY rank ASC;"
    )
    rows = cursor.fetchall()
    return list(map(lambda x: x[0], rows))


@with_db
def add_target(cursor, coin_name: str, ticker_name: str):
    """
    코인 추가
    """
    try:
        cursor.execute(
            "INSERT INTO coin (coin_name, ticker_name) VALUES (?, ?);",
            (coin_name, ticker_name),
        )
    except sqlite3.IntegrityError:
        pass


@with_db
def update_active(cursor, id: int, is_active: int):
    """
    코인 활성화 여부 수정
    """
    cursor.execute("UPDATE coin SET is_active = ? WHERE id = ?;", (is_active, id))
