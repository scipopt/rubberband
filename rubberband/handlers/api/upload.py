"""Contains UploadApiEndpoint."""
import logging
from tornado.escape import json_encode
from tornado.ioloop import IOLoop
from tornado.gen import coroutine

from .base import BaseHandler, authenticated
from rubberband.utils import ResultClient, write_file, sendmail
from rubberband.utils.importer import bundle_files


class UploadAsyncEndpoint(BaseHandler):
    """Request handler handling the upload by api asynchronously."""

    @authenticated
    @coroutine
    def put(self):
        """
        Answer to PUT requests.

        The method that is called to upload files, spawn a callback to import_files.
        Write json response.
        """
        files = self.request.files.values()
        tags = self.get_argument("tags", [])

        IOLoop.current().spawn_callback(import_files, files, tags, self.current_user,
                                        self.application.base_url)
        self.set_status(202)  # Accepted
        json_response = make_response("queued", self.application.base_url, msg="Check your inbox.")

        self.write(json_response)


class UploadEndpoint(BaseHandler):
    """Request handler handling the upload by api."""

    @authenticated
    def put(self):
        """
        Answer to PUT requests.

        The method that rbcli calls to upload files via commandline.
        Write json response.
        """
        files = self.request.files.values()
        tags = self.get_argument("tags", [])
        expirationdate = self.get_argument("expirationdate", None)
        results = perform_import(files, tags, self.current_user, expirationdate=expirationdate)

        self.set_status(201)  # created
        for result in results:
            if result.fail:
                self.set_status(400)  # bad request
                break

        response = []
        for result in results:
            if result.fail:
                response.append(make_response(result.status, self.application.base_url,
                                 basename=result.basename, errors=result.getMessages()))
            else:
                url = "{}{}".format(self.application.base_url, result.getUrl())
                response.append(make_response(result.status, url, basename=result.basename))

        self.write(json_encode(response))


@coroutine
def import_files(paths, tags, user, url_base, expirationdate=None):
    """
    Pass everything to import and report result back.

    Parameters
    ----------
    paths : list of str
        paths to files
    tags : str
        list of tags
    user : str
        username
    url_base : str
        base url for response
    expirationdate : str
        expirationdate

    Sends an email to user after successfull import.
    """
    results = perform_import(paths, tags, user, expirationdate=expirationdate)

    response = []
    for result in results:
        if result.fail:
            response.append(make_response(result.status, url_base,
                                     basename=result.basename, errors=result.getMessages()))
        else:
            url = "{}{}".format(url_base, result.getUrl())
            response.append(make_response(result.status, url=url, basename=result.basename))

    logging.info("Sending an email to {}".format(user))
    sendmail(response, user)


def perform_import(files, tags, user, expirationdate=None):
    """
    Preform the import.

    Parameters
    ----------
    files : list of str
        The files to be imported
    tags : str or list
        The tags associated to the files
    user : str
        The username
    expirationdate : str
        The expirationdate

    Returns
    -------
    ImportStats
        result of import
    """
    paths = []
    for f in files:
        paths.append(write_file(f[0]["filename"], f[0]["body"]))

    if tags != []:
        tags = tags.split(",")
        tags = list(map(str.strip, tags))

    bundles = bundle_files(paths)

    importstats = []
    for bundle in bundles:
        c = ResultClient(user=user)
        c_stat = c.process_files(bundle, tags=tags, expirationdate=expirationdate)
        importstats.append(c_stat)

    return importstats


def make_response(status, url, basename="", msg="", errors=""):
    """
    Construct a response dictionary.

    Parameters
    ----------
    status : str
        Status
    url : str
        URL
    basename : str
        basename of file
    msg : str
        Message
    errors : str
        Errors

    Returns
    -------
    dict
        contains keys "status", "url", optional "msg", "errors".
    """
    response = {
        "status": status,
        "url": url,
    }
    if msg:
        response["msg"] = msg
    if errors:
        response["errors"] = errors
    if basename:
        response["basename"] = basename

    return response
