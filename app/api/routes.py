import datetime

from flask import jsonify, request

from app import app
from app.models import *
from app.utils import find_shortest_intervals, calc_dict_difference, three_months_from_now
from app.api.errors import bad_request


@app.route("/api/", methods=["GET"])
def api_index():
    tickers = Ticker.query.all()
    tickers = [ticker.to_dict() for ticker in tickers]
    return jsonify(tickers=tickers)


@app.route("/api/<ticker_name>", methods=["GET"])
def api_ticker(ticker_name):
    date = three_months_from_now()
    ticker = Ticker.query.filter_by(name=ticker_name).first()
    history = History.query.filter(History.ticker_id == ticker.id, History.date >= date).all()
    history = [row.to_dict() for row in history]
    return jsonify(history=history)


@app.route("/api/<ticker_name>/insiders", methods=["GET"])
def api_insiders(ticker_name):
    ticker = Ticker.query.filter_by(name=ticker_name).first()
    insiders = Insider.query.filter_by(ticker_id=ticker.id).all()
    insiders = [insider.to_dict() for insider in insiders]
    return jsonify(insiders=insiders)


@app.route("/api/<ticker_name>/insiders/<insider_name>", methods=["GET"])
def api_insider(ticker_name, insider_name):
    insider_data = Insider.query.filter_by(name=insider_name).all()
    insider_data = [insider.to_dict() for insider in insider_data]
    return jsonify(insider_data=insider_data)


@app.route("/api/<ticker_name>/analytics", methods=["GET"])
def api_analytics(ticker_name):
    start_date = request.args.get("date_from")
    end_date = request.args.get("date_to")

    try:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    except:
        return bad_request(message="Введенные даты не корректны")

    first = History.query.filter_by(date=start_date).first()
    second = History.query.filter_by(date=end_date).first()

    if not first or not second:
        return bad_request(message="Одной из дат нет в базе данных.")

    first = first.to_dict()
    second = second.to_dict()
    difference = calc_dict_difference(first, second, ["date"])
    return jsonify(first=first, second=second, difference=difference)


@app.route("/api/<ticker_name>/delta", methods=["GET"])
def api_delta(ticker_name):
    value = request.args.get("value")

    try:
        value = int(value)
    except ValueError:
        return bad_request(message="Недопустимый атрибут")

    delta_type = request.args.get("type")
    ticker = Ticker.query.filter_by(name=ticker_name).first()
    history_data = History.query.filter_by(ticker_id=ticker.id).order_by(History.date.asc()).all()

    if not hasattr(history_data[0], delta_type):
        return bad_request(message="Недопустимый атрибут")

    shortest_intervals = find_shortest_intervals(history_data=history_data, delta_type=delta_type, threshold=value)
    return jsonify(intervals=shortest_intervals)
