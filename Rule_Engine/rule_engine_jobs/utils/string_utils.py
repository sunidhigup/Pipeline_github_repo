def is_string_null(value):
    """
        Method to check if string value is null
        :param value: It is a value used to match with conditions in return statement
        :return boolean value: return true if string value is null or None
    """
    return (value is None) or value in ["NULL", "Null", "null"]


def is_full_string(value):
    """
        Method to check if given value is string or not
        :param value: It is a value used to check return condition
        :return boolean value: return true if value is string
    """
    return isinstance(value, str) and value.strip() != ""


def is_string_true(value):
    """
        Method to get boolean value based on given condition
        :param value: It is a value used to match with conditions in return statement
        :return boolean value: return true if value is True and not equals to None and blank
    """
    return is_full_string(value) and value in ["True", "TRUE", "true"]


def compare_ignore_case(str1: str, str2: str) -> bool:
    """
    compare 2 strings, ignoring the case of stings
    :param str1: string 1
    :type str1: str
    :param str2: string 2
    :type str2: str
    :return: bool
    """
    return str1.casefold() == str2.casefold()

