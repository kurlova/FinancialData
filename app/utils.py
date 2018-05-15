DATETIME_FORMAT = "%m/%d/%Y"


def datetimeformat(value):
    """
    Фильтр для Jinja2, который отображает datetime-объект в необходимом формате
    :param value: datetime объект
    :return: строка указанного формата
    """
    return value.strftime(DATETIME_FORMAT)
