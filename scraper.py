import argparse
import datetime
import re
import requests
import threading
import traceback
import sys
import os

from bs4 import BeautifulSoup as bs
from queue import Queue
import time

from app import db
from app.models import History, Ticker, Insider, InsiderTrade


TICKERS_FILENAME = os.path.join(os.getcwd(), "tickers.txt")


def save_to_db(object):
    with db_writer_lock:
        db.session.add(object)
        db.session.commit()


def get_or_create_object(modelname, **kwargs):
    """
    Если запись уже присутствует в базе данных, возвращаем ее идентификатор
    В противном случае создаем запись и рекурсивно получаем ее идентификатор

    :param modelname: модель, по которой ищем запись
    :param kwargs: поля, которые идентифицируют запись
    :return: id сущесвтующей записи или вызов самой себя для поиска только что созданной записи
    """
    obj = modelname.query.filter_by(**kwargs).first()
    if obj:
        return obj
    else:
        save_to_db(modelname(**kwargs))
        return get_or_create_object(modelname, **kwargs)


class ScrapingManager:
    def __init__(self, threads):
        self.threads = threads

    @property
    def tickers(self):
        """
        Получает список всех акций из файла-источника

        :param filename: имя файла
        :return: список из названий акций
        """
        with open(TICKERS_FILENAME, "r") as f:
            tickers = f.readlines()

        return [ticker.rstrip('\n') for ticker in tickers]

    def assign_parallel_processes(self):
        for thread in range(self.threads):
            t = threading.Thread(target=self.do_work)
            t.daemon = True
            t.start()

        try:
            for ticker in self.tickers:
                q.put(ticker)
            q.join()
        except KeyboardInterrupt:
            sys.exit(1)

    def do_work(self):
        while True:
            ticker = q.get()
            self.process_ticker(ticker)
            q.task_done()

    def process_ticker(self, ticker):
        try:
            print(threading.current_thread().name, ticker)
            ticker_obj = get_or_create_object(Ticker, name=ticker)
            history_scraper = HistoryScraper(ticker=ticker_obj)
            history_scraper.process()
            trader_scraper = InsiderTradesScraper(ticker=ticker_obj)
            trader_scraper.process()
        except Exception:
            print("Processed with error:")
            traceback.print_exc()


class BaseScraper:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36"
    }
    base_url = "http://www.nasdaq.com/symbol/{}/{}"

    def __init__(self, ticker_obj):
        self.ticker_id = ticker_obj.id
        self.ticker_name = ticker_obj.name

    def get_start_url(self, url_path):
        return self.base_url.format(self.ticker_name.lower(), url_path)

    @staticmethod
    def convert_to_int(string):
        """
        Конвертация в int для хранения записи в базе данных
        :param string: число в виде строки, может содержать запятые (пример: 10,000 или 0)
        :return: int или None (если строка пустая)
        """
        if string:
            return int(string.replace(',', ''))
        return None

    @staticmethod
    def convert_to_float(string):
        """
        Конвертация в float для хранения записи в базе данных
        :param string: число в виде строки, может содержать точку (пример: 84.9600)
        :return: float или None (если строка пустая)
        """
        if string:
            return float(string)
        return None

    @staticmethod
    def convert_to_datetime(string):
        """
        Конвертация в datetime для хранения записи в базе данных
        :param string: строка, может представлять дату (05/11/2018) или время (16:00)
        :return: datetime или None (если строка пустая)
        """
        full_pattern = re.compile("\d+/\d+/\d+")  # найдет соответствия таким строкам как: 05/11/2018
        hours_pattern = re.compile("\d+:\d+")  # найдет соответствия таким строкам как: 16:00

        if full_pattern.match(string):
            return datetime.datetime.strptime(string, "%m/%d/%Y")
        elif hours_pattern.match(string):
            hour, minute = string.split(':')
            return datetime.datetime.now().replace(hour=int(hour), minute=int(minute), second=0, microsecond=0)
        else:
            return None


class HistoryScraper(BaseScraper):
    url_path = 'historical'

    def __init__(self, ticker):
        super().__init__(ticker)

    def process(self):
        url = self.get_start_url(self.url_path)

        try:
            self.process_page(url)
        except Exception as e:
            print(f"Exception occured on page {url}")
            traceback.print_exc()

    def process_page(self, url):
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            print('Bad response')
            return

        soup = bs(response.content, "html.parser")
        data_container = soup.find("div", {"id": "historicalContainer"})
        data_table = data_container.find("table").find("tbody")
        rows = data_table.find_all("tr")[1:]

        for row in rows:
            cells = row.find_all("td")
            date = self.convert_to_datetime(cells[0].text.strip())
            open = self.convert_to_float(cells[1].text)
            high = self.convert_to_float(cells[2].text)
            low = self.convert_to_float(cells[3].text)
            close = self.convert_to_float(cells[4].text)
            volume = self.convert_to_int(cells[5].text)

            history_obj = History(date=date, open=open, high=high, low=low, close=close, volume=volume,
                                  ticker_id=self.ticker_id)
            save_to_db(history_obj)


class InsiderTradesScraper(BaseScraper):
    url_path = 'insider-trades'
    max_pages = 10  # максимальное число страниц пагинатора, с которых будут собираться данные

    def __init__(self, ticker):
        super().__init__(ticker)

    def process(self):
        url = self.get_start_url(self.url_path)

        try:
            self.process_page(url)
        except Exception as e:
            print(f"Exception occured on page {url}")
            traceback.print_exc()

    def process_page(self, url):
        response = requests.get(url, headers=self.headers)

        if response.status_code != 200:
            print('Bad response')
            return

        soup = bs(response.content, "html.parser")
        data_table = soup.find("div", {"class": "genTable"})
        rows = data_table.find_all("tr")[1:]  # нет <tbody>, поэтому не обрабатываем 1ю строку с заголовками таблицы

        for row in rows:
            cells = row.find_all("td")
            name = cells[0].text
            inner_id = self.convert_to_int(cells[0].find("a")["href"].split("-")[-1])
            relation = cells[1].text
            last_date = self.convert_to_datetime(cells[2].text)
            transaction_type = cells[3].text
            owner_type = cells[4].text
            shares_traded = self.convert_to_int(cells[5].text)
            last_price = self.convert_to_float(cells[6].text)
            shares_held = self.convert_to_int(cells[7].text)

            insider_obj = get_or_create_object(Insider, name=name, relation=relation, inner_id=inner_id,
                                               ticker_id=self.ticker_id)
            insider_trade_obj = InsiderTrade(insider_id=insider_obj.id, last_date=last_date,
                                  transaction_type=transaction_type, owner_type=owner_type, shares_traded=shares_traded,
                                  last_price=last_price, shares_held=shares_held)
            save_to_db(insider_trade_obj)

        pager_ul = soup.find("ul", {"id": "pager"})
        last_span = pager_ul.find_all("span")[-1]
        last_span_parent = last_span.parent
        next_page = last_span_parent.nextSibling

        if not next_page:
            return

        next_page = next_page.find("a")["href"]
        next_num = int(re.search("page=(\d+)", next_page).group(1))

        if next_num <= self.max_pages:
            return self.process_page(next_page)
        else:
            return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Укажите число потоков')
    parser.add_argument('--threads', type=int)
    args = parser.parse_args()

    if args.threads:
        threads_num = args.threads
    else:
        threads_num = 3

    start = time.time()
    q = Queue()
    db_writer_lock = threading.Lock()
    sm = ScrapingManager(threads_num)
    sm.assign_parallel_processes()
    print(time.time() - start)

