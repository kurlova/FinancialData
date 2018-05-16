import datetime

from unittest import TestCase
from unittest.mock import patch

from app.models import History, Ticker
from app.utils import generate_sequences, find_min_intervals


class TestDelta(TestCase):

    def test_find_intervals(self):
        history_data = [History(date=datetime.datetime(2018, 5, 4), open=125.21, high=126.84, low=124.71,
                                     close=125.53, volume=5400810),
                             History(date=datetime.datetime(2018, 5, 7), open=126.59, high=128.4, low=124.44,
                                     close=124.94, volume=6999937),
                             History(date=datetime.datetime(2018, 5, 8), open=124.93, high=126.75, low=123.63,
                                     close=126.57, volume=8882661),
                             History(date=datetime.datetime(2018, 5, 9), open=128.42, high=130.42, low=128.085,
                                     close=128.72, volume=11395850)
                             ]
        # ticker_name = "CVX"
        value = 2
        delta_type = "open"
        # ticker = Ticker.query.filter_by(name=ticker_name).first()
        # history_data = History.query.filter_by(ticker_id=ticker.id).order_by(History.date.asc()).all()[-6:-2]
        print(history_data)
        all_sequences_gen = generate_sequences(history_data, delta_type)
        min_intervals = find_min_intervals(all_sequences_gen, value)
        print('min_intervals', min_intervals)
