import os
import sys
from pathlib import Path
import unittest
from unittest import mock

from flask import Flask


BASE_DIR = Path(__file__).resolve().parents[1]
APP_DIR = BASE_DIR / "app"
sys.path.insert(0, str(APP_DIR))

os.environ.setdefault("POSTGRES_DB", "test_master")
os.environ.setdefault("POSTGRES_USER", "test_user")
os.environ.setdefault("POSTGRES_PASSWORD", "test_pass")
os.environ.setdefault("SKIP_DB_INIT", "1")

import util.api as api


class ApiSessionTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)

    def test_get_sessions_requires_branch(self):
        with self.app.test_request_context():
            with mock.patch("util.api.find_auth", return_value=None):
                res = api.getSessions()
        self.assertEqual(res.status_code, 400)

    def test_get_sessions_from_cookie(self):
        with self.app.test_request_context(headers={"Cookie": "branch=N24"}):
            with mock.patch("util.api.get_sessions", return_value=[[11, 2024]]):
                res = api.getSessions()
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.get_json(), [[11, 2024]])


if __name__ == "__main__":
    unittest.main()
