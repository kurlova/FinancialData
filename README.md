# FinancialData

Веб-сервис, который собирает данные с сайта Nasdaq и отображает имеющуюся информацию

Инструменты: Python3.6, Flask (сервер), requests/BeautifulSoup (скрапер)

Запустить сервис с помощью Docker:

```docker-compose up --build``` из папки проекта

зайти в контейнер приложения:

```
docker exec -it <"python app.py" container id> bash

cd app
```

написать:
```
flask db init
flask db migrate
flask db upgrade
python scraper.py --threads=N (или просто python scraper.py)
```

подождать пока скрипт выполнится, выйти из контейнера:
```exit```

зайти в браузере на ```127.0.0.1:5000```