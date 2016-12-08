from tornado.web import RequestHandler, HTTPError
from tornado.options import options
import traceback
import functools
import logging


class BaseHandler(RequestHandler):
    '''
    Custom overrides.
    '''
    def get_current_user(self):
        if not self.settings["debug"]:
            headers = dict(self.request.headers.get_all())
            token = headers.get("X-Api-Token")
            if token and token == options.api_token:
                return headers.get("X-Forwarded-Email")
        else:
            return "debug"

    def write_error(self, status_code, **kwargs):
        if self.settings.get("serve_traceback") and "exc_info" in kwargs:
            # in debug mode, try to send a traceback
            self.set_header('Content-Type', 'text/plain')
            for line in traceback.format_exception(*kwargs["exc_info"]):
                self.write(line)
        else:
            self.write({"message": "{} {}".format(status_code, self._reason)})

        self.finish()


def authenticated(method):
    """
    Decorate methods with this to require that the user to have been authenticated
    """
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        if not self.current_user:
            logging.error("User not authorized: {}".format(self.current_user))
            raise HTTPError(401)
        return method(self, *args, **kwargs)
    return wrapper
