
def boolify(value):
    '''
    Convert a string to a bool, if not possible, raise a ValueError.
    '''
    if value.lower() == "true":
        return True
    elif value.lower() == "false":
        return False
    raise ValueError("{} is not a bool".format(value))

def estimate_type(var):
    '''
    Guesses the str representation of the variables type
    Example:

    >>> estimate_type("3.0")
    3.0
    >>> type(estimate_type("3.0"))
    <class 'float'>
    >>> estimate_type("true")
    True
    >>> type(estimate_type("true"))
    <class 'bool'>
    '''
    var = str(var)

    for caster in (boolify, int, float):
        try:
            return caster(var)
        except ValueError:
            pass
    return var
