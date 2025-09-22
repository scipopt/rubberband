"""Contains ErrorView."""

from .base import BaseHandler
from tornado.web import HTTPError


class ErrorView(BaseHandler):
    """Request handler handling the error pages."""

    def prepare(self):
        """
        Prepare, always gets called before answering to a specific request.

        Raises an HTTPError
        """
        raise HTTPError(404)
