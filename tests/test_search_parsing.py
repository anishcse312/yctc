import os
import sys
from pathlib import Path
import unittest

from flask import Flask


BASE_DIR = Path(__file__).resolve().parents[1]
APP_DIR = BASE_DIR / "app"
sys.path.insert(0, str(APP_DIR))

os.environ.setdefault("POSTGRES_DB", "test_master")
os.environ.setdefault("POSTGRES_USER", "test_user")
os.environ.setdefault("POSTGRES_PASSWORD", "test_pass")
os.environ.setdefault("SKIP_DB_INIT", "1")

import util.search as search


class SearchParsingTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)

    def test_parse_branch_from_reg(self):
        self.assertEqual(search.parse_branch_from_reg("YS-N24/35-3300356/2013"), "N24")
        self.assertEqual(search.parse_branch_from_reg("N24/35-3300356/2013"), "N24")
        self.assertIsNone(search.parse_branch_from_reg(None))

    def test_resolve_branch_from_cookie(self):
        with self.app.test_request_context(headers={"Cookie": "branch=N24"}):
            self.assertEqual(search.resolve_branch_from_cookie(), "N24")


if __name__ == "__main__":
    unittest.main()
