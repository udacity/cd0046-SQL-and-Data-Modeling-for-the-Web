import re


def is_valid_phone(number: str):
    regex = re.compile(r'^\(?[0-9]{3}\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$')
    return regex.match(number)
