
from ..exceptions import ChangeRequestException
from logging import getLogger
from traceback import format_exc
logger = getLogger(__name__)


def raise_and_log_exception(exception=None):
    """Decorator to raise provided exception on error and log it.

    This decorator is useful when functions/methods want to wrap their
    code in a try/except to handle errors. By using this decorator, it uplifts
    the additional changes needed in a function. (e.g. less indentation). \

    :param class exception: the exception class to raise
    """
    def wrapper(func):
        """Wrapper function accepting the function to decorate.

        :param function func: function to invoke
        """
        def wrapped(*args, **kwargs):
            """Invoke the function and raise exception provided on error.

            :param tuple args: multiple arguments
            :param dict kwargs: keyword arguments
            """
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if exception:
                    logger.error(format_exc())
                    logger.error(e)
                    raise exception(e)
                else:
                    logger.error(format_exc())
                    logger.error(ChangeRequestException(exc=e))
                    raise ChangeRequestException(exc=e)
        return wrapped
    return wrapper
