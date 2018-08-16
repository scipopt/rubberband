"""Contains HelpView."""
from .base import BaseHandler


class HelpView(BaseHandler):
    """Request handler holding the help page."""

    def get(self):
        """
        Answer to GET requests.

        Renders `help.html`.
        """
        questions = {
            "What is Rubberband?":
                "Rubberband is a flexible web view and analysis platform for solver log files of mathematical optimization software, backed by Elasticsearch.", # noqa
            "Where do i report errors and other issues?":
                "Rubberband is a project developed on GitHub, you can post your issue <a href='https://github.com/ambros-gleixner/rubberband/issues'>here</a>.", # noqa
            }

        self.render("help.html", questions=questions, page_title="Help")
