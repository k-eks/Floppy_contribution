from decimal import *
import re


def error_string_to_decimal(string):
    """
    Changes a string number such as 1.23(4) into 1.23 and 0.004.
    :param string: string, which gets converted
    :return: (decimal, decimal), value and error
    """
    string = string.strip()
    value = 0
    error = 0
    if '(' in string:
        precission = string.index('.')
        length = string.index('(')
        value = Decimal(string[:length])
        error = Decimal(string[length+1:-1]) * Decimal(10) ** Decimal(-(length - precission - 1))
    else:
        value = Decimal(string)
    return value, error


def atom_name_sort(x):
    """
    Used in conjunction with AtomData objects to sort them by name.
    :param x: AtomData, by which to sort
    :return: function, key for the sorted statement
    """
    sort = re.search(r'([A-Z]+)(\d+)',x.name)
    return sort.group(1), int(sort.group(2))