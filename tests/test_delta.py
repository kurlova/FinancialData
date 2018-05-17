import datetime

from unittest import TestCase

from app.models import History
from app.utils import find_shortest_intervals


class TestDelta(TestCase):

    def test_find_intervals(self):
        value = 2
        delta_type = "open"
        mock_history_data = [History(date=datetime.datetime(2018, 5, 4), open=125.21, high=126.84, low=124.71,
                                     close=125.53, volume=5400810, ticker_id=1),
                             History(date=datetime.datetime(2018, 5, 7), open=126.59, high=128.4, low=124.44,
                                     close=124.94, volume=6999937, ticker_id=1),
                             History(date=datetime.datetime(2018, 5, 8), open=124.93, high=126.75, low=123.63,
                                     close=126.57, volume=8882661, ticker_id=1),
                             History(date=datetime.datetime(2018, 5, 9), open=128.42, high=130.42, low=128.085,
                                     close=128.72, volume=11395850, ticker_id=1)
                             ]
        print(mock_history_data)
        shortest = find_shortest_intervals(history_data=mock_history_data, delta_type=delta_type, threshold=value)
        self.assertEqual(shortest, [{'delta': 3.4899999999999807,
                                     'start': datetime.datetime(2018, 5, 8, 0, 0),
                                     'end': datetime.datetime(2018, 5, 9, 0, 0),
                                     'length': 1}])
