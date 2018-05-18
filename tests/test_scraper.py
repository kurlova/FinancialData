import datetime
from unittest import TestCase
from freezegun import freeze_time

from scraper import BaseScraper
from app.models import Ticker


class TestBaseScraper(TestCase):
    ticker = Ticker(id=0, name="SOMEABBR")

    def setUp(self):
        self.scraper = BaseScraper(ticker_obj=self.ticker)

    def test_convert_fulldate_to_datetime(self):
        fulldate = "05/11/2018"
        date = self.scraper.convert_to_datetime(fulldate)
        self.assertEqual(date, datetime.datetime(2018, 5, 11))

    @freeze_time("2018-05-11")
    def test_convert_shortdate_to_datetime(self):
        shortdate = "16:00"
        date = self.scraper.convert_to_datetime(shortdate)
        self.assertEqual(date, datetime.datetime(2018, 5, 11, 16, 0))

    def test_convert_empty_to_datetime(self):
        date = self.scraper.convert_to_datetime("")
        self.assertIs(date, None)

    def test_convert_to_int(self):
        num1 = self.scraper.convert_to_int("8,091,770")
        num2 = self.scraper.convert_to_int("")
        num3 = self.scraper.convert_to_int("0")
        self.assertEqual(num1, 8091770)
        self.assertEqual(num2, None)
        self.assertEqual(num3, 0)

    def test_convert_to_float(self):
        num1 = self.scraper.convert_to_float("129.84")
        num2 = self.scraper.convert_to_float("")
        num3 = self.scraper.convert_to_float("0.0000")
        self.assertEqual(num1, 129.84)
        self.assertEqual(num2, None)
        self.assertEqual(num3, 0.0)
