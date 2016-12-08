import logging
from tornado.escape import json_encode
from tornado.ioloop import IOLoop
from tornado.gen import coroutine

from .base import BaseHandler, authenticated
from rubberband.utils import ResultClient, write_file, sendmail


class UploadAsyncEndpoint(BaseHandler):
    @authenticated
    @coroutine
    def put(self):
        files = self.request.files.values()
        tags = self.get_argument("tags", [])

        IOLoop.current().spawn_callback(import_files, files, tags, self.current_user,
                                        self.application.base_url)
        self.set_status(202)  # Accepted
        json_response = make_response("queued", self.application.base_url, msg="Check your inbox.")

        self.write(json_response)


class UploadEndpoint(BaseHandler):
    @authenticated
    def put(self):
        '''
        The method that rbcli calls to upload files via commandline.
        '''
        files = self.request.files.values()
        tags = self.get_argument("tags", [])
        results = perform_import(files, tags, self.current_user)

        if results.fail:
            self.set_status(400)  # bad request
            response = make_response(results.status, self.application.base_url,
                                     errors=results.getMessages())
        else:
            self.set_status(201)  # created
            url = "{}{}".format(self.application.base_url, results.getUrl())
            response = make_response(results.status, url)

        self.write(json_encode(response))


@coroutine
def import_files(paths, tags, user, url_base):
    results = perform_import(paths, tags, user)
    fail = results.fail
    if fail:
        response = make_response(results.status, url_base,
                                 errors=results.getMessages())
    else:
        url = "{}{}".format(url_base, results.getUrl())
        response = make_response(results.status, url=url)

    logging.info("Sending an email to {}".format(user))
    sendmail(response, user)


def perform_import(files, tags, user):
    paths = []
    for f in files:
        paths.append(write_file(f[0]["filename"], f[0]["body"]))
    paths = tuple(paths)

    if tags != []:
        tags = tags.split(",")
        tags = list(map(str.strip, tags))

    c = ResultClient(user=user)
    return c.process_files(paths, tags=tags)


def make_response(status, url, msg="", errors=""):
    response = {
        "status": status,
        "url": url,
    }
    if msg:
        response["msg"] = msg
    if errors:
        response["errors"] = errors

    return response
