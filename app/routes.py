import datetime

from flask import render_template, redirect, url_for, request, flash, abort

from app import app
from app.models import Ticker, History, Insider
from app.forms import DateForm, DeltaForm
from app.utils import find_shortest_intervals, calc_dict_difference, three_months_from_now


def get_or_404(modelname, **kwargs):
    obj = modelname.query.filter_by(**kwargs).first()
    if not obj:
        return abort(404)
    return obj


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.route("/", methods=["GET"])
def index():
    tickers = Ticker.query.all()
    tickers = [ticker.to_dict() for ticker in tickers]
    return render_template("index.html", tickers=tickers)


@app.route("/<ticker_name>", methods=["GET", "POST"])
def ticker(ticker_name):
    date = three_months_from_now()
    ticker = get_or_404(Ticker, name=ticker_name)
    history = History.query.filter(History.ticker_id == ticker.id, History.date >= date).all()
    history = [row.to_dict() for row in history]

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


@app.route("/<ticker_name>/insider", methods=["GET"])
def insiders(ticker_name):
    ticker = get_or_404(Ticker, name=ticker_name)
    insiders = Insider.query.filter_by(ticker_id=ticker.id).all()
    insiders = [insider.to_dict() for insider in insiders]
    return render_template("insiders.html", ticker=ticker, insiders=insiders)


@app.route("/<ticker_name>/insider/<insider_name>", methods=["GET"])
def insider(ticker_name, insider_name):
    ticker = get_or_404(Ticker, name=ticker_name)
    insider_data = get_or_404(Insider, name=insider_name)
    insider_data = insider_data.to_dict()
    return render_template("insider_data.html", ticker=ticker, insider=insider_data)


@app.route("/<ticker_name>/analytics", methods=["GET"])
def analytics(ticker_name):
    ticker = get_or_404(Ticker, name=ticker_name)
    start_date = request.args.get("date_from")
    end_date = request.args.get("date_to")

    try:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    except:
        flash("Введенные даты не корректны")
        return redirect(url_for("ticker", ticker_name=ticker_name))

    first = get_or_404(History, date=start_date)
    second = get_or_404(History, date=end_date)
    first = first.to_dict()
    second = second.to_dict()
    difference = calc_dict_difference(first, second, ["date"])

    return render_template("analytics.html", ticker=ticker, first=first,
                           second=second, difference=difference)


@app.route("/<ticker_name>/delta", methods=["GET", "POST"])
def delta(ticker_name):
    value = request.args.get("value")

    try:
        value = int(value)
    except ValueError:
        flash("Недопустимый тип атрибута value")
        return redirect(url_for("ticker", ticker_name=ticker_name))

    delta_type = request.args.get("type")
    ticker = get_or_404(Ticker, name=ticker_name)
    history_data = History.query.filter_by(ticker_id=ticker.id).order_by(History.date.asc()).all()

    if not hasattr(history_data[0], delta_type):
        flash(f"Недопустимый атрибут {delta_type}")
        return redirect(url_for("ticker", ticker_name=ticker_name))

    shortest_intervals = find_shortest_intervals(history_data=history_data, delta_type=delta_type, threshold=value)

    delta_form = DeltaForm()
    if delta_form.validate_on_submit():
        delta_val = delta_form.value.data
        delta_type = delta_form.type.data
        return redirect(url_for("delta", ticker_name=ticker_name, value=delta_val, type=delta_type))

    return render_template("intervals.html", ticker=ticker, value=value, type=delta_type,
                           intervals=shortest_intervals, delta_form=delta_form)
