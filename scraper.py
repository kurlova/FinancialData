import datetime
import re
import requests

from bs4 import BeautifulSoup as bs

from app import db
from app.models import History, Insider, Ticker


TICKERS_FILENAME = "tickers.txt"


class ScrapingManager:
    def __init__(self, threads=1):
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

        for ticker in tickers:
            yield ticker.rstrip("\n")

    @staticmethod
    def save_to_db(object):
        db.session.add(object)
        db.session.commit()

    def get_or_create_new(self, modelname, **kwargs):
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
            self.save_to_db(modelname(**kwargs))
            self.get_or_create_new(modelname, **kwargs)

    def scrape(self):
        for ticker in self.tickers:
            # добавить ticker в базу данных
            ticker_obj = self.get_or_create_new(Ticker, name=ticker)

            history_scraper = HistoryScraper(ticker=ticker_obj)
            history_scraper.process()
            trader_scraper = InsiderTradesScraper(ticker=ticker_obj)
            trader_scraper.process()


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

    def get_ticker_id(self):
        pass


class HistoryScraper(BaseScraper):
    url_path = 'historical'

    def __init__(self, ticker):
        super().__init__(ticker)

    def process(self):
        url = self.get_start_url(self.url_path)
        self.process_page(url)

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
            db.session.add(history_obj)
            db.session.commit()


class InsiderTradesScraper(BaseScraper):
    url_path = 'insider-trades'
    max_pages = 10  # максимальное число страниц пагинатора, с которых будут собираться данные

    def __init__(self, ticker):
        super().__init__(ticker)

    def process(self):
        url = self.get_start_url(self.url_path)
        self.process_page(url)

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

            insider_obj = Insider(name=name, inner_id=inner_id, relation=relation, last_date=last_date,
                                  transaction_type=transaction_type, owner_type=owner_type, shares_traded=shares_traded,
                                  last_price=last_price, shares_held=shares_held, ticker_id=self.ticker_id)
            db.session.add(insider_obj)
            db.session.commit()

        pager_ul = soup.find("ul", {"id": "pager"})
        last_span = pager_ul.find_all("span")[-1]
        last_span_parent = last_span.parent
        next_page = last_span_parent.nextSibling

        if not next_page:
            print("Pages are over")
            return

        next_page = next_page.find("a")["href"]
        next_num = int(re.search("page=(\d+)", next_page).group(1))

        if next_num <= self.max_pages:
            return self.process_page(next_page)
        else:
            return


if __name__ == "__main__":
    sm = ScrapingManager()
    sm.scrape()

