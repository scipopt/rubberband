
from .base import BaseHandler
from tornado import gen, web, httpclient, websocket
import logging, logging.handlers
import time

logger = logging.getLogger(__name__)

sockethandler = logging.handlers.SocketHandler('localhost',
        logging.handlers.DEFAULT_TCP_LOGGING_PORT)
#sockethandler = logging.handlers.SocketHandler()
sockethandler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
sockethandler.setFormatter(formatter)

logger.addHandler(sockethandler)

def log(iterations=3):
    logger.info("new round")
    logger.info("hallo welt, {} speaking.".format(__name__))
    for i in range(iterations):
        out = "iteration {}".format(i)
        logger.info(out)
        time.sleep(1)

class TestSocketHandler(websocket.WebSocketHandler):

    def open(self):
        print("Socket opened")

    def on_close(self):
        print("WebSocket closed")

    def on_message(self, message):
        self.write_message(u"Received {}".format(message))
        log()

#from .base import BaseHandler
#from tornado import gen, web, httpclient
#import logging
#import time
#from io import StringIO
#
###### LOGGING
#log_stream = StringIO()
#
#logger = logging.getLogger(__name__)
#
#logsubset = logging.StreamHandler(log_stream)
#logsubset.setLevel(logging.INFO)
#formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#logsubset.setFormatter(formatter)
#
#logger.addHandler(logsubset)
#
#def log(iterations=3):
#    logger.info("hallo welt, {} speaking.".format(__name__))
#    for i in range(iterations):
#        out = "iteration {}".format(i)
#        logger.info(out)
#        print(out)
#        time.sleep(1)

class TestView(BaseHandler):

    def get(self):
        url = "http://127.0.0.1:8888/testsocket"

        conn = yield websocket_connect(url)
        while True:
            msg = yield conn.read_message()
            if msg is None:
                break
            self.write(msg)
            self.flush()

    #def get(self):
    #    log()
    #    #self.render("test.html", page_title="test", content=log_stream.getvalue())

    #    self.write("hello.")
    #    self.flush()
    #    character = None
    #    for line in log_stream.getvalue():
    #        self.write(line)
    #        self.flush()

    #    log_stream.flush()
    #    self.write(log_stream.getvalue())

    #    self.write('done')
    #    self.flush()
