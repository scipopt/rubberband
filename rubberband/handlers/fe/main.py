"""Contains MainView."""
from .base import BaseHandler


class MainView(BaseHandler):
    """Request handler handling the main view."""

    def get(self):
        """
        Answer to GET requests.

        Home view. This is redirected to SearchView at the moment.
        """
        # 301 permanent redirect
        self.redirect("search", status=301)
