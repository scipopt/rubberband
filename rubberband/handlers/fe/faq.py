from .base import BaseHandler


class FAQView(BaseHandler):
    def get(self):
        # The logfiles are not stored in integer/runlogs
        self.render("faq.html", page_title="Frequently Asked Questions")
