from .base import BaseHandler


class HelpView(BaseHandler):
    def get(self):
        # The logfiles are not stored in integer/runlogs
        self.render("help.html", page_title="Help")
