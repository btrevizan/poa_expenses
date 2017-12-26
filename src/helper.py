from time import mktime
from pandas import read_csv
from datetime import datetime


def read(filepath, fields, sep=';', decimal=','):
    """Read, select columns and clear data.

    Keyword arguments:
        filepath -- path to file
        fields -- list of column indexes
        sep -- separator (default ';')
        decimal -- decimal separatore (default ',')
    """
    data = read_csv(filepath, sep=sep, decimal=decimal)
    data = data.iloc[:, fields]

    return data


def clear(data):
    """Clear string and format dates.

    Keyword argument:
        data -- a DataFrame
    """
    n, m = data.shape

    # For each type of data (columns has same type in every line)
    for j in range(m):
        sample = data.iloc[0, j]

        if len(str(sample).split('-')) == 3:
            dtype = to_date
        elif type(sample) is str:
            dtype = to_str
        else:
            dtype = lambda x: x

        # For each line in column j
        for i in range(n):
            data.iloc[i, j] = dtype(data.iloc[i, j])

    return data


def to_date(value):
    """Convert string to timestamp.

    Keyword argument:
        value -- value to be converted
    """
    y, m, d = value.split('-')
    d, _ = d.split('T')

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
