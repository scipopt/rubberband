"""Contains ErrorView."""
from .base import BaseHandler
from tornado.web import ErrorHandler


class ErrorView(BaseHandler, ErrorHandler):
    """
    Request handler handling the errors pages.

    write_error is defined in BaseHandler, the rest is done by ErrorHandler
    """
    pass
