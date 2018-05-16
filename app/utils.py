DATETIME_FORMAT = "%m/%d/%Y"


def datetimeformat(value):
    """
    Фильтр для Jinja2, который отображает datetime-объект в необходимом формате
    :param value: datetime объект
    :return: строка указанного формата
    """
    return value.strftime(DATETIME_FORMAT)


def calc_delta_value(seq, delta_type):
    delta = 0

    if len(seq) == 0:
        return delta

    for index in range(1, len(seq)):
        prev = seq[index - 1]
        curr = seq[index]
        if delta_type == "open":
            delta += curr.open - prev.open
        elif delta_type == "high":
            delta += curr.high - prev.high
        elif delta_type == "low":
            delta += curr.low - prev.low
        else:
            delta += curr.close - prev.close

    return delta


def dates_consecutive(prev_date, date):
    """
    Выполняем проверку на то, что даты последовательны и отличаются не более чем на 1 день
    Т.к. может быть такое, что после какой-либо даты отсутствует следующий день
    :param prev_date: предыдущая дата
    :param date: дата
    :return: True, если разница между двумя датами не более 1 дня, False в противном случае
    """
    return abs((date - prev_date).days) <= 1


def create_subsequence(start, end, data):
    subsequence = []

    for subseq_index in range(start, end):
        data_element = data[subseq_index]
        # формируем подпоследовательность
        subsequence.append(data_element)
    return subsequence


def generate_sequences(data, delta_type):
    sequences = []
    n = len(data)

    for data_element_index in range(n):
        # берем каждый элемент списка data последовательно
        start_seq_index = data_element_index  # индекс начала подпоследовательности (минимум)
        end_seq_index = n  # индекс окончания подпоследовательности (максимум)

        for subseq_len in range(start_seq_index + 1, end_seq_index + 1):
            # проходимся по возможному количеству элементов в последовательности
            subsequence = create_subsequence(start_seq_index, subseq_len, data)

            if len(subsequence) > 1:
                # не рассматриваем последовательности из одной даты
                delta_value = calc_delta_value(subsequence, delta_type)
                subseq_tuple = (delta_value, list(map(lambda x: x.date, subsequence)))

                # if subseq_tuple not in sequences:
                sequences.append(subseq_tuple)

    for subseq in sequences:
        yield subseq


def find_min_intervals(sequences, border_value):
    """
    Находит минимальные временные интервалы с разницей цены акции более или равной заданному значению
    :param intervals: все доступные интервалы
    :param border_value: минимальное значение изменения цены
    :return: список с минимальными интервалами
    """
    min_intervals = list()

    for seq in sequences:
        # print(seq)
        interval = Interval(seq[0], seq[1][0], seq[1][-1])
        interval_len = interval.length

        if interval.delta >= border_value:
            if len(min_intervals) == 0:
                min_intervals.append(interval)
            else:
                # считаем разницу в днях у последнего элемента min_interval_len
                last_min = min_intervals[-1]
                min_interval_len = last_min.length

                if min_interval_len > interval_len:
                    # нашли интервал с меньшей длиной
                    min_intervals = list()
                    min_intervals.append(interval)
                elif min_interval_len == interval_len:
                    # нашли интервал с такой же длиной, что и у уже добавленного интервала
                    min_intervals.append(interval)
                else:
                    continue

    return min_intervals


class Interval:
    """
    Представляет собой временной интервал
    """
    def __init__(self, delta, start, end):
        """
        :param delta: изменение цены в пределах интервала
        :param start: начало интервала (объект datetime)
        :param end: конец интервала (объект datetime)
        """
        self.delta = delta
        self.start = start
        self.end = end

    @property
    def length(self):
        """
        Длина в днях между началом и концом интервала
        :return:
        """
        return abs(self.start - self.end).days

    def __repr__(self):
        return f"<Interval: delta={self.delta}, start={self.start}, end={self.end}>"
