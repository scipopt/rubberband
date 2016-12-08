import tornado.web

from .base import BaseHandler, authenticated


class MiscEndpoint(BaseHandler):
    @authenticated
    def get(self):
        '''
        Return 404
        '''
        raise tornado.web.HTTPError(404)
