FROM python:3.6
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["app.py"]
RUN flask db init
RUN flask db migrate
RUN flask db upgrade
RUN python scraper.py