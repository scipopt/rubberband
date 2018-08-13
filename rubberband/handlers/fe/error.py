"""Contains ErrorView."""
from .base import BaseHandler
from tornado.web import HTTPError


class ErrorView(BaseHandler):
    """Request handler handling the error pages."""

    def prepare(self):
        """
        Always gets called before answering to a spectific request.

        Raises an HTTPError
        """
        raise HTTPError(404)
