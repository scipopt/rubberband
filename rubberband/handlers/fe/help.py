"""Contains HelpView."""
from .base import BaseHandler


class HelpView(BaseHandler):
    """Request handler holding the help page."""

    def get(self):
        """
        Answer to GET requests.

        Renders `help.html`.
        """
        self.render("help.html", page_title="Help")
