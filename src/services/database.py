# -*- coding: utf-8 -*-
"""Lưu trữ danh bạ tạm thời bằng SQLite để xem trước không cần nạp hết vào RAM."""
import os
import sqlite3
from contextlib import closing

from src.services.settings import appDataDir

DEFAULT_DB_FILE = 'contacts_data.db'


def defaultDbPath(dbFile: str = DEFAULT_DB_FILE) -> str:
    """Đặt CSDL tạm trong thư mục temp của người dùng.

    KHÔNG đặt cạnh file thực thi: thư mục cài đặt có thể chỉ-đọc (Program Files),
    và file này chứa dữ liệu danh bạ (PII) nên không nên nằm chung với ứng dụng.
    """
    return os.path.join(appDataDir(), dbFile)


class DatabaseManager:
    """Quản lý cơ sở dữ liệu SQLite lưu trữ danh bạ."""

    def __init__(self, dbFile: str = None):
        self.dbFile = dbFile or defaultDbPath()
        self._setupDatabase()

    def _getConn(self):
        """`with sqlite3.connect(...)` chỉ commit/rollback — bọc closing() để đóng hẳn."""
        return closing(sqlite3.connect(self.dbFile))

    def _setupDatabase(self):
        with self._getConn() as conn, conn:
            conn.cursor().execute('''
                CREATE TABLE IF NOT EXISTS contacts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL, number TEXT NOT NULL, email TEXT,
                    organization TEXT, address TEXT, birthday TEXT, notes TEXT,
                    status TEXT DEFAULT 'success', original_row INTEGER
                )
            ''')
            conn.commit()

    def clearAllContacts(self):
        with self._getConn() as conn, conn:
            conn.cursor().execute("DELETE FROM contacts")
            conn.commit()

    def addContact(self, data: dict):
        with self._getConn() as conn, conn:
            conn.cursor().execute('''
                INSERT INTO contacts (name, number, email, organization, address, birthday, notes, status, original_row)
                VALUES (:name, :number, :email, :organization, :address, :birthday, :notes, :status, :original_row)
            ''', data)
            conn.commit()

    def getContactCount(self) -> int:
        with self._getConn() as conn, conn:
            return conn.cursor().execute("SELECT COUNT(id) FROM contacts").fetchone()[0]

    def getContactsPaginated(self, page: int, pageSize: int) -> list:
        with self._getConn() as conn, conn:
            conn.row_factory = sqlite3.Row
            offset = (page - 1) * pageSize
            return conn.cursor().execute(
                "SELECT * FROM contacts ORDER BY original_row LIMIT ? OFFSET ?",
                (pageSize, offset),
            ).fetchall()
