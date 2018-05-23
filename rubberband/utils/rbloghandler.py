"""Class for a RequestHandler to respond with logoutput from loggering module."""
from logging import StreamHandler
import hashlib
import time


class RBLogHandler(StreamHandler):
    """A handler for the logging module passing the information stream like to obj.write."""

    def __init__(self, handle):
        """
        Given a handle (i.e. a tornado.RequestHandler), write logging output to the aforementioned.

        Introduce yourself with a hash as stamp to mark where logoutput begins.

        Parameters
        ----------
        handle : obj
            any stream like object writing with obj.write()
            and flushing with obj.flush().
        """
        StreamHandler.__init__(self)
        rawname = "rbhandler{}{}".format(time.time(), handle)
        self.name = hashlib.md5(bytes(rawname, 'utf-8')).hexdigest()
        self.rbhandle = handle
        self.rbwrite(self.name)

    def flush(self):
        """Flush the emitted output."""
        self.rbhandle.flush()

    def emit(self, record):
        """
        Emit the emitted output.

        Parameters
        ----------
        record : LogRecord
            output to emit
        """
        msg = self.format(record)
        if "Validation information provided:" not in msg:
            self.rbwrite(msg + "\n")

    def rbwrite(self, msg):
        """
        Write out the msg with the handle and flush.

        Parameters
        ----------
        msg : str
            output to write
        """
        self.rbhandle.write(msg)
        self.flush()

    def close(self):
        """Close the handler, not the handle with a hash as stamp to mark where logoutput ends."""
        self.rbwrite(self.name)
        StreamHandler.close(self)

    def __repr__(self):
        """Return an identification string."""
        return "RBLogHandler ({}, {})".format(self.name, self.level)
