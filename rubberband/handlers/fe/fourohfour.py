"""Contains FourOhFourView."""
from .base import BaseHandler


class FourOhFourView(BaseHandler):
    """Request handler handling the 404 page."""

    def get(self):
        """
        Answer to GET requests.

        Used by Tornado as default_handler_class.
        Renders `404.html`
        """
        self.set_status(404)
        self.render("404.html")
