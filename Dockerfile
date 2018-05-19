FROM python:3.6
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
#ENV FLASK_APP app.py
#CMD ["-m", "flask", "db", "init"]
#CMD ["-m", "flask", "db", "migrate"]
#CMD ["-m", "flask", "db", "upgrade"]
CMD ["app.py"]