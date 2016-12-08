from .base import BaseHandler


class FAQView(BaseHandler):
    def get(self):
        self.render("faq.html", page_title="Frequently Asked Questions")
