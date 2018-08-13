"""Contains HelpView."""
from .base import BaseHandler


class UserView(BaseHandler):
    """Request handler holding the personal user page."""

    def get(self):
        """
        Answer to GET requests.

        Renders `help.html`.
        """
        mycookies = {}

        self.set_cookie("one", "uno")
        self.set_cookie("two", "dos")

        mycookies["one"] = self.get_cookie("one")
        mycookies["two"] = self.get_cookie("two")

        self.render("basket.html", mycookies=mycookies, page_title="Personal space")
