# starting from this file

import os
import tornado.ioloop
import tornado.httpserver

from rubberband.boilerplate import make_app, options

KB = 1024
MB = 1024 * KB
GB = 1024 * MB


def main():
    project_root = os.path.join(os.path.dirname(__file__), "rubberband")
    app = make_app(project_root)
    # create an HTTPServer
    server = tornado.httpserver.HTTPServer(
        app, max_body_size=2 * GB, max_buffer_size=2 * GB
    )
    # bind it to a port specified in 'options'
    server.bind(options.port)
    # start server and ioloop as main event loop
    server.start(options.num_processes)
    tornado.ioloop.IOLoop.current().start()


if __name__ == "__main__":
    main()
