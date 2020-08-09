from django.db.models import ExpressionWrapper, Func, Value, F, CharField
from django.db.models.functions import Concat

from utils.relativedelta import relativedelta


def get_period_expression(period, field_name):
    date_format = {'daily': '%Y-%m-%d', 'weekly': '%W Week', 'monthly': '%Y-%m', 'yearly': '%Y'}
    period_exp = ExpressionWrapper(
        Func(Value(date_format.get(period) or '%Y'), F(field_name), function='strftime'),
        output_field=CharField()
    )

    return period_exp


def gen_dates(b_date, days, delta, date_format=None):
    for i in range(days):
        result = b_date + delta * i
        if date_format:
            yield result.strftime(date_format)
        else:
            yield '{}Q{}'.format(result.year, (result.month - 1) // 3 + 1)


def get_date_range(period, start, end):
    data = []
    if period == 'daily':
        delta = relativedelta(days=1)
        date_format = '%Y-%m-%d'
        durations = (end - start).days + 1
    elif period == 'monthly':
        delta = relativedelta(months=1)
        date_format = '%Y-%m'
        durations = end.month - start.month + 1 + (end.year - start.year) * 12
    elif period == 'yearly':
        delta = relativedelta(years=1)
        date_format = '%Y'
        durations = end.year - start.year + 1
    else:
        delta = relativedelta(months=3)
        date_format = None
        durations = (end.year - start.year) * 4 + ((end.month - 1) // 3) - ((start.month - 1) // 3) + 1
    for d in gen_dates(start, durations, delta, date_format):
        data.append(d)
    return data

