class DataError(Exception):
    """Raised when the data is not imported properly"""

    pass


class BudgetExhausted(Exception):
    """The budget has been exhausted; stop immediately"""

    pass
