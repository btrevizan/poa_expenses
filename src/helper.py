from time import mktime
from datetime import datetime


def to_date(value):
    """Convert string to timestamp.

    Keyword argument:
        value -- value to be converted
    """
    y, m, d = value.split('-')
    d = d[:2]

    date = datetime.strptime('{}-{}-{}'.format(y, m, d), '%Y-%m-%d')
    timestamp = mktime(date.timetuple())

    return int(timestamp)


def to_str(value):
    """Clear string.

    Keyword argument:
        value -- value to be cleaned
    """
    value = value.strip()
    value = value.upper()

    return value


def to_parts(value):
    """Split string by space.

    Keyword argument:
        value -- value to be divided
    """
    value = to_str(value)                          # strip 'n upper
    values = value.split(' ')                      # split
    values = filter(lambda x: len(x) > 3, values)  # remove stop word

    return list(values)
