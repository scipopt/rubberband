from .base import BaseHandler


class FourOhFourView(BaseHandler):
    '''
    404 Handler
    '''
    def get(self):
        self.set_status(404)
        self.render("404.html")
