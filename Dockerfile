FROM python3.6

COPY FinancialData COPY /bin/

RUN pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT python __init__.py