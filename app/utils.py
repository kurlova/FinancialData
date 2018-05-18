import datetime

from dateutil.relativedelta import relativedelta


DATETIME_FORMAT = "%m/%d/%Y"


def datetimeformat(value):
    """
    Фильтр для Jinja2, который отображает datetime-объект в необходимом формате
    :param value: datetime объект
    :return: строка указанного формата
    """
    return value.strftime(DATETIME_FORMAT)


def calc_sum(subseq, delta_type):
    """
    Суммирует все разницы цен для данной последовательности
    Например, для последовательности:
    [<History object: 2018-05-09 00:00:00-128.42-130.42-128.085-128.72-11395850>,
    <History object: 2018-05-10 00:00:00-129.69-129.81-128.39-128.82-5444773>,
    <History object: 2018-05-08 00:00:00-124.93-126.75-123.63-126.57-8882661>]
    с типом "open"
    посчитает (129.69 - 128.42) + (124.93 - 129.69)
    :param subseq: последовательность интервалов
    :param delta_type: строка, тип цены акции (равна строковому представлению соответствующего атрибута)
    :return: сумму соответствующих значений
    """
    return sum([getattr(subseq[el], delta_type) - getattr(subseq[el - 1], delta_type)
                for el in range(len(subseq)) if el > 0])


def find_shortest_intervals(history_data, delta_type, threshold):
    """
    Находит самые короткие интервалы времени,
    за которые указанная цена акции менялась на или более чем на заданное значение
    :param history_data: список с объектами History, история изменения цен
    :param delta_type: строка, по какому атрибуту осуществляется поиск (low/high/close/last)
    :param threshold: int, минимальное значение изменения цены
    :return: список словарей для подходящих интервалов
    """
    intervals = []

    for day_index in range(len(history_data)):
        for interval_index in range(day_index + 1, len(history_data) + 1):
            subsequence = history_data[day_index:interval_index]
            delta = calc_sum(subsequence, delta_type)
            delta = round(delta, 2)

            if delta >= threshold:
                intervals.append(dict(delta=delta,
                                      start=subsequence[0].date,
                                      end=subsequence[-1].date,
                                      length=(subsequence[-1].date - subsequence[0].date).days))

    min_days = min(interval["length"] for interval in intervals)
    shortest = [interval for interval in intervals if interval["length"] == min_days]
    return shortest


def calc_dict_difference(first, second, excluded_keys):
    """
    Вычитает значения одного словаря из другого, пропуская указанные ключи
    :param first: словарь, из которого вычитаем значения
    :param second: словарь, который вычитаем
    :param excluded_keys: ключи, которые не учитываются
    :return:
    """
    return {key: round(first[key] - second.get(key, 0), 2) for key in first.keys() if key not in excluded_keys}


def three_months_from_now():
    """
    Считает дату три месяца назад от сегодняшнего дня
    :return: соответствующий datetime
    """
    today = datetime.datetime.today().replace(hour=0, minute=0, second=0, microsecond=0)
    return today - relativedelta(months=3)