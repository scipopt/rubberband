"""Contains HelpView."""
from .base import BaseHandler


class UserView(BaseHandler):
    """Request handler holding the personal user page."""

    def get(self):
        """
        Answer to GET requests.

        Renders `help.html`.
        """
        #self.set_cookie("one", "uno")
        #self.set_cookie("two", "dos")

        self.clear_all_cookies()

        self.render("basket.html", mycookies=self.get_all_cookies(), page_title="Personal space")


