import datetime
from dateutil.relativedelta import relativedelta

from app import app
from flask import render_template, jsonify, redirect, url_for, request, flash

from app.models import *
from app.forms import DateForm, DeltaForm
from app.utils import generate_sequences, find_min_intervals


@app.route("/", methods=["GET"])
def index():
    tickers = Ticker.query.all()
    return render_template("index.html", tickers=tickers)


@app.route("/<ticker_name>", methods=["GET", "POST"])
def ticker(ticker_name):
    today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    three_months_from_now = today - relativedelta(months=3)
    ticker = Ticker.query.filter_by(name=ticker_name).first()
    history = History.query.filter(History.ticker_id == ticker.id, History.date >= three_months_from_now).all()

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


@app.route("/<ticker_name>/insiders", methods=["GET"])
def insiders(ticker_name):
    ticker = Ticker.query.filter_by(name=ticker_name).first()
    insiders = Insider.query.filter_by(ticker_id=ticker.id).all()
    return render_template("insiders.html", ticker=ticker, insiders=insiders)


@app.route("/<ticker_name>/insiders/<insider_name>-<insider_inner_id>", methods=["GET"])
def insider(ticker_name, insider_name, insider_inner_id):
    ticker = Ticker.query.filter_by(name=ticker_name).first()
    insider_data = Insider.query.filter_by(inner_id=insider_inner_id).all()
    return render_template("insider_data.html", ticker=ticker, insider_data=insider_data)


@app.route("/<ticker_name>/analytics", methods=["GET"])
def analytics(ticker_name):
    ticker = Ticker.query.filter_by(name=ticker_name).first()
    start_date = request.args.get("date_from")
    end_date = request.args.get("date_to")

    try:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    except:
        flash("Введите корректные даты")
        return redirect(url_for("ticker", ticker_name=ticker_name))

    first = History.query.filter_by(date=start_date).first()
    second = History.query.filter_by(date=end_date).first()

    if not first or not second:
        if not first:
            flash(f"Даты {start_date} нет в базе данных.")
        if not second:
            flash(f"Даты {end_date} нет в базе данных.")
        return redirect(url_for("ticker", ticker_name=ticker_name))

    return render_template("analytics.html", ticker=ticker, first=first, second=second)


@app.route("/<ticker_name>/delta", methods=["GET", "POST"])
def delta(ticker_name):
    value = request.args.get("value")
    value = int(value)
    delta_type = request.args.get("type")
    print(value, delta_type)
    ticker = Ticker.query.filter_by(name=ticker_name).first()
    history_data = History.query.filter_by(ticker_id=ticker.id).order_by(History.date.asc()).all()
    all_sequences_gen = generate_sequences(history_data, delta_type)
    min_intervals = find_min_intervals(all_sequences_gen, value)

    delta_form = DeltaForm()
    if delta_form.validate_on_submit():
        delta_val = delta_form.value.data
        delta_type = delta_form.type.data
        return redirect(url_for("delta", ticker_name=ticker_name, value=delta_val, type=delta_type))

    return render_template("intervals.html", ticker=ticker, value=value, type=delta_type,
                           intervals=min_intervals, delta_form=delta_form)