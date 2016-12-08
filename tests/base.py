import os
from tornado.testing import AsyncHTTPTestCase

from rubberband.boilerplate import make_app

# add application root to sys.path
APP_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PACKAGE_ROOT = os.path.join(APP_ROOT, "rubberband")

app = make_app(PACKAGE_ROOT)


class TestHandlerBase(AsyncHTTPTestCase):
    def get_app(self):
        return app
