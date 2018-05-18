import datetime

from flask import jsonify, request, abort

from app.models import Ticker, History, Insider
from app.utils import find_shortest_intervals, calc_dict_difference, three_months_from_now
from app.api import bp
from app.api.errors import bad_request


def get_or_404(modelname, **kwargs):
    obj = modelname.query.filter_by(**kwargs).first()
    if not obj:
        print('return bad request')
        return abort(404)
    return obj


@bp.errorhandler(404)
def page_not_found(e):
    return bad_request(404)


@bp.route("/", methods=["GET"])
def index():
    tickers = Ticker.query.all()
    tickers = [ticker.to_dict() for ticker in tickers]
    return jsonify(tickers=tickers)


@bp.route("/<ticker_name>", methods=["GET"])
def ticker(ticker_name):
    date = three_months_from_now()
    ticker = get_or_404(Ticker, name=ticker_name)
    history = History.query.filter(History.ticker_id == ticker.id, History.date >= date).all()
    history = [row.to_dict() for row in history]
    return jsonify(history=history)


@bp.route("/<ticker_name>/insider", methods=["GET"])
def insiders_trades(ticker_name):
    ticker = get_or_404(Ticker, name=ticker_name)
    insiders = Insider.query.filter_by(ticker_id=ticker.id).all()
    insiders = [insider.to_dict() for insider in insiders]
    return jsonify(insiders=insiders)


@bp.route("/<ticker_name>/insider/<insider_name>", methods=["GET"])
def insider(ticker_name, insider_name):
    insider_data = get_or_404(Insider, name=insider_name)
    insider_data = insider_data.to_dict()
    return jsonify(insider=insider_data)


@bp.route("/<ticker_name>/analytics", methods=["GET"])
def analytics(ticker_name):
    start_date = request.args.get("date_from")
    end_date = request.args.get("date_to")

    try:
        start_date = datetime.datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(end_date, "%Y-%m-%d")
    except:
        return bad_request(400, message="Введенные даты не корректны")

    first = get_or_404(History, date=start_date)
    second = get_or_404(History, date=end_date)
    first = first.to_dict()
    second = second.to_dict()
    difference = calc_dict_difference(first, second, ["date"])
    return jsonify(first=first, second=second, difference=difference)


@bp.route("/<ticker_name>/delta", methods=["GET"])
def delta(ticker_name):
    value = request.args.get("value")

    try:
        value = int(value)
    except ValueError:
        return bad_request(400, message="Недопустимый тип атрибута value")

    delta_type = request.args.get("type")
    ticker = Ticker.query.filter_by(name=ticker_name).first()
    history_data = History.query.filter_by(ticker_id=ticker.id).order_by(History.date.asc()).all()

    if not hasattr(history_data[0], delta_type):
        return bad_request(400, message=f"Недопустимый атрибут {delta_type}")

    shortest_intervals = find_shortest_intervals(history_data=history_data, delta_type=delta_type, threshold=value)
    return jsonify(intervals=shortest_intervals)
