FROM python:3.6
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD sleep 30 && flask db init && flask db migrate && flask db upgrade && python scraper.py && python app.py