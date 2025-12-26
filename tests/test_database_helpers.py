import os
import sys
from contextlib import contextmanager
from pathlib import Path
import unittest
from unittest import mock


BASE_DIR = Path(__file__).resolve().parents[1]
APP_DIR = BASE_DIR / "app"
sys.path.insert(0, str(APP_DIR))

os.environ.setdefault("POSTGRES_DB", "test_master")
os.environ.setdefault("POSTGRES_USER", "test_user")
os.environ.setdefault("POSTGRES_PASSWORD", "test_pass")
os.environ.setdefault("SKIP_DB_INIT", "1")

import util.database as db


class FakeCursor:
    def __init__(self, fetchone_values=None):
        self.executed = []
        self._fetchone_values = iter(fetchone_values or [])

    def execute(self, query, params=None):
        self.executed.append((query, params))

    def fetchone(self):
        return next(self._fetchone_values, None)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class FakeConn:
    def __init__(self, fetchone_values=None):
        self.autocommit = False
        self._fetchone_values = fetchone_values or []
        self.last_cursor = None

    def cursor(self, **_kwargs):
        self.last_cursor = FakeCursor(self._fetchone_values)
        return self.last_cursor

    def commit(self):
        return None


class DatabaseHelperTests(unittest.TestCase):
    def test_branch_db_name(self):
        self.assertEqual(db.branch_db_name("N24"), "yctc_N24")

    def test_session_table_name(self):
        self.assertEqual(db.session_table_name(11, "stuadmn"), "11_stuadmn")

    def test_create_database_if_missing_noop_when_exists(self):
        fake_conn = FakeConn(fetchone_values=[(1,)])

        @contextmanager
        def fake_get_conn(_db_name):
            yield fake_conn

        with mock.patch("util.database.get_conn", fake_get_conn):
            db.create_database_if_missing("yctc_N24")

        self.assertEqual(len(fake_conn.last_cursor.executed), 1)
        self.assertFalse(fake_conn.autocommit)

    def test_create_database_if_missing_creates(self):
        fake_conn = FakeConn(fetchone_values=[None])

        @contextmanager
        def fake_get_conn(_db_name):
            yield fake_conn

        with mock.patch("util.database.get_conn", fake_get_conn):
            db.create_database_if_missing("yctc_N24")

        self.assertEqual(len(fake_conn.last_cursor.executed), 2)
        self.assertFalse(fake_conn.autocommit)

    def test_ensure_data_table_executes(self):
        fake_conn = FakeConn(fetchone_values=[None])

        @contextmanager
        def fake_get_conn(_db_name):
            yield fake_conn

        with mock.patch("util.database.get_conn", fake_get_conn):
            db.ensure_data_table("yctc_N24", "11_stuadmn", ["reg_no", "name"])

        self.assertEqual(len(fake_conn.last_cursor.executed), 1)


if __name__ == "__main__":
    unittest.main()
