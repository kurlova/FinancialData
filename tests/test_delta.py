import datetime

from unittest import TestCase

from app.models import History
from app.utils import find_shortest_intervals


class TestDelta(TestCase):
    def setUp(self):
        self.history = [History(date=datetime.datetime(2018, 5, 4), open=125.21, high=126.84, low=124.71,
                                     close=125.53, volume=5400810, ticker_id=1),
                             History(date=datetime.datetime(2018, 5, 7), open=126.59, high=128.4, low=124.44,
                                     close=124.94, volume=6999937, ticker_id=1),
                             History(date=datetime.datetime(2018, 5, 8), open=124.93, high=126.75, low=123.63,
                                     close=126.57, volume=8882661, ticker_id=1),
                             History(date=datetime.datetime(2018, 5, 9), open=128.42, high=130.42, low=128.085,
                                     close=128.72, volume=11395850, ticker_id=1)
                             ]

    def test_find_intervals_open(self):
        value = 2
        delta_type = "open"
        shortest = find_shortest_intervals(history_data=self.history, delta_type=delta_type, threshold=value)
        self.assertEqual(shortest, [{'delta': 3.49,
                                     'start': datetime.datetime(2018, 5, 8, 0, 0),
                                     'end': datetime.datetime(2018, 5, 9, 0, 0),
                                     'length': 1}])

    def test_intervals_close(self):
        value = 2
        delta_type = "close"
        shortest = find_shortest_intervals(history_data=self.history, delta_type=delta_type, threshold=value)
        self.assertEqual(shortest, [{'delta': 2.15,
                                     'start': datetime.datetime(2018, 5, 8, 0, 0),
                                     'end': datetime.datetime(2018, 5, 9, 0, 0),
                                     'length': 1}])

    def test_intervals_high(self):
        value = 2
        delta_type = "high"
        shortest = find_shortest_intervals(history_data=self.history, delta_type=delta_type, threshold=value)
        self.assertEqual(shortest, [{'delta': 3.67,
                                     'start': datetime.datetime(2018, 5, 8, 0, 0),
                                     'end': datetime.datetime(2018, 5, 9, 0, 0),
                                     'length': 1}])

    def test_intervals_low(self):
        value = 2
        delta_type = "low"
        shortest = find_shortest_intervals(history_data=self.history, delta_type=delta_type, threshold=value)
        self.assertEqual(shortest, [{'delta': 4.46,
                                     'start': datetime.datetime(2018, 5, 8, 0, 0),
                                     'end': datetime.datetime(2018, 5, 9, 0, 0),
                                     'length': 1}])

    def test_zero_intervals_open(self):
        value = 10
        delta_type = "open"
        shortest = find_shortest_intervals(history_data=self.history, delta_type=delta_type, threshold=value)
        self.assertEqual(shortest, [])

    def test_negative_value_open(self):
        """
        Предположительно, отрицательный value не имеет ввиду то, что ищем разницу "в обратную сторону",
        т.е. результат не подразумевает "меньше отрицательного", а всегда больше.
        """
        value = -1
        delta_type = "open"
        shortest = find_shortest_intervals(history_data=self.history, delta_type=delta_type, threshold=value)
        self.assertEqual(shortest, [
            {'delta': 0, 'start': datetime.datetime(2018, 5, 4, 0, 0), 'end': datetime.datetime(2018, 5, 4, 0, 0), 'length': 0},
            {'delta': 0, 'start': datetime.datetime(2018, 5, 7, 0, 0), 'end': datetime.datetime(2018, 5, 7, 0, 0), 'length': 0},
            {'delta': 0, 'start': datetime.datetime(2018, 5, 8, 0, 0), 'end': datetime.datetime(2018, 5, 8, 0, 0), 'length': 0},
            {'delta': 0, 'start': datetime.datetime(2018, 5, 9, 0, 0), 'end': datetime.datetime(2018, 5, 9, 0, 0), 'length': 0}
        ])
