import datetime
from dateutil.relativedelta import relativedelta

from app import app
from flask import render_template, jsonify, redirect, url_for, request, flash

from app.models import *
from app.forms import DateForm, DeltaForm
from app.utils import find_shortest_intervals


def get_all_tickers():
    tickers = Ticker.query.all()
    return [dict(id=ticker.id, name=ticker.name) for ticker in tickers]


def get_ticker(**kwargs):
    return Ticker.query.filter_by(**kwargs).first()


def get_ticker_history(ticker_name):
    today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    three_months_from_now = today - relativedelta(months=3)
    ticker = get_ticker(name=ticker_name)
    history = History.query.filter(History.ticker_id == ticker.id, History.date >= three_months_from_now).all()
    return [dict(id=row.id, date=row.date, open=row.open, high=row.high, low=row.low,
                 close=row.close, volume=row.volume, ticker_id=row.ticker_id)
        for row in history]


def get_insiders(ticker_name):
    ticker = get_ticker(name=ticker_name)
    insiders = Insider.query.filter_by(ticker_id=ticker.id).all()
    return [dict(id=insider.id, name=insider.name, inner_id=insider.inner_id,
                 relation=insider.relation, last_date=insider.last_date,
                 transaction_type=insider.transaction_type, owner_type=insider.owner_type,
                 shares_traded=insider.shares_traded, last_price=insider.last_price,
                 shares_held=insider.shares_held, ticker_id=insider.ticker_id) for insider in insiders]


@app.route("/", methods=["GET"])
def index():
    tickers = get_all_tickers()
    return render_template("index.html", tickers=tickers)


@app.route("/api/", methods=["GET"])
def api_index():
    tickers = get_all_tickers()
    return jsonify(tickers=tickers)


@app.route("/<ticker_name>", methods=["GET", "POST"])
def ticker(ticker_name):
    ticker = get_ticker(name=ticker_name)
    history = get_ticker_history(ticker_name)

    date_form = DateForm()
    if date_form.validate_on_submit():
        start_date = date_form.start_date.data
        end_date = date_form.end_date.data
        return redirect(url_for("analytics", ticker_name=ticker_name, date_from=start_date, date_to=end_date))

    delta_form = DeltaForm()
    if delta_form.validate_on_submit():
        delta_val = delta_form.value.data
        delta_type = delta_form.type.data
        return redirect(url_for("delta", ticker_name=ticker_name, value=delta_val, type=delta_type))

    return render_template("ticker_history.html", ticker=ticker, history=history,
                           date_form=date_form, delta_form=delta_form)


@app.route("/api/<ticker_name>", methods=["GET"])
def api_ticker(ticker_name):
    ticker_history = get_ticker_history(ticker_name)
    return jsonify(ticker_history=ticker_history)


@app.route("/<ticker_name>/insiders", methods=["GET"])
def insiders(ticker_name):
    ticker = get_ticker(name=ticker_name)
    insiders = get_insiders(ticker_name)
    return render_template("insiders.html", ticker=ticker, insiders=insiders)


@app.route("/api/<ticker_name>/insiders", methods=["GET"])
def api_insiders(ticker_name):
    insiders = get_insiders(ticker_name)
    return jsonify(insiders=insiders)


def get_insider_operations(name):
    operations = Insider.query.filter_by(name=name).all()
    return [dict(id=row.id, name=row.name, inner_id=row.inner_id,
                 relation=row.relation, last_date=row.last_date,
                 transaction_type=row.transaction_type, owner_type=row.owner_type,
                 shares_traded=row.shares_traded, last_price=row.last_price,
                 shares_held=row.shares_held, ticker_id=row.ticker_id) for row in operations]


@app.route("/<ticker_name>/insiders/<insider_name>", methods=["GET"])
def insider(ticker_name, insider_name, insider_inner_id):
    ticker = get_ticker(name=ticker_name)
    insider_data = get_insider_operations(insider_inner_id)
    return render_template("insider_data.html", ticker=ticker, insider_data=insider_data)


@app.route("/api/<ticker_name>/insiders/<insider_name>", methods=["GET"])
def api_insider(ticker_name, insider_name):
    insider_data = get_insider_operations(insider_name)
    return jsonify(insider_data=insider_data)


def get_history_row(date):
    row = History.query.filter_by(date=date).first()
    return dict(id=row.id, date=row.date, open=row.open, high=row.high, low=row.low,
                 close=row.close, volume=row.volume, ticker_id=row.ticker_id)


def calc_dict_difference(first, second, excluded_keys):
    return {key: round(first[key] - second.get(key, 0), 2) for key in first.keys() if key not in excluded_keys}


@app.route("/<ticker_name>/analytics", methods=["GET"])
def analytics(ticker_name):
    ticker = Ticker.query.filter_by(name=ticker_name).first()
    start_date = request.args.get("date_from")
    end_date = request.args.get("date_to")

    try:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    except:
        flash("Введенные даты не корректны")
        return redirect(url_for("ticker", ticker_name=ticker_name)), 422

    first = get_history_row(start_date)
    second = get_history_row(end_date)

    if not first or not second:
        flash("Одной из дат нет в базе данных."), 404
        return redirect(url_for("ticker", ticker_name=ticker_name))

    difference = calc_dict_difference(first, second, ["date"])

    return render_template("analytics.html", ticker=ticker, first=first,
                           second=second, difference=difference)


@app.route("/api/<ticker_name>/analytics", methods=["GET"])
def api_analytics(ticker_name):
    start_date = request.args.get("date_from")
    end_date = request.args.get("date_to")

    try:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    except:
        return jsonify(data="Введенные даты не корректны"), 422

    first = get_history_row(start_date)
    second = get_history_row(end_date)

    if not first or not second:
        return jsonify(data="Одной из дат нет в базе данных."), 404

    difference = calc_dict_difference(first, second, ["date"])
    return jsonify({"first": first, "second": second, "difference": difference}), 200


@app.route("/<ticker_name>/delta", methods=["GET", "POST"])
def delta(ticker_name):
    value = request.args.get("value")
    value = int(value)
    delta_type = request.args.get("type")
    ticker = Ticker.query.filter_by(name=ticker_name).first()
    history_data = History.query.filter_by(ticker_id=ticker.id).order_by(History.date.asc()).all()

    if not hasattr(history_data[0], delta_type):
        flash(f"Такого типа цен ({delta_type}) нет.")
        return redirect(url_for("ticker", ticker_name=ticker_name))

    shortest_intervals = find_shortest_intervals(history_data=history_data, delta_type=delta_type, threshold=value)

    delta_form = DeltaForm()
    if delta_form.validate_on_submit():
        delta_val = delta_form.value.data
        delta_type = delta_form.type.data
        return redirect(url_for("delta", ticker_name=ticker_name, value=delta_val, type=delta_type))

    return render_template("intervals.html", ticker=ticker, value=value, type=delta_type,
                           intervals=shortest_intervals, delta_form=delta_form)


@app.route("/api/<ticker_name>/delta", methods=["GET"])
def api_delta(ticker_name):
    value = request.args.get("value")
    value = int(value)
    delta_type = request.args.get("type")
    ticker = Ticker.query.filter_by(name=ticker_name).first()
    history_data = History.query.filter_by(ticker_id=ticker.id).order_by(History.date.asc()).all()

    if not hasattr(history_data[0], delta_type):
        return jsonify(data="Недопустимый атрибут"), 422

    shortest_intervals = find_shortest_intervals(history_data=history_data, delta_type=delta_type, threshold=value)
    return jsonify(intervals=shortest_intervals), 200