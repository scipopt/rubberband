
#from .base import BaseHandler
#from tornado import gen, web, httpclient, websocket
#import logging
#from logging import StreamHandler
#import time
#
#logger = logging.getLogger(__name__)
#
#class RBHandler(StreamHandler):
#
#    def __init__(self, handle):
#        StreamHandler.__init__(self)
#        self.rbhandle = handle
#
#    def flush(self):
#        self.rbhandle.flush()
#
#    def emit(self, record):
#        msg = self.format(record)
#        self.rbhandle.write(msg)
#        self.flush()
#
#    def __repr__(self):
#        return "rb handler ({}, {})".format(name, level)
#
#class TestView(BaseHandler):
#
#    def get(self):
#        rbhandler = RBHandler(self)
#
#        rbhandler.setLevel(logging.INFO)
#        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#        rbhandler.setFormatter(formatter)
#
#        logger.addHandler(rbhandler)
#
#        log()
#
#        #self.render("test.html", page_title="test", content=log_stream.getvalue())
#        logger.removeHandler(rbhandler)
#        rbhandler.close()
#
#        self.finish()
#
