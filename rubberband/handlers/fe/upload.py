"""Contains UploadView."""
from rubberband.utils import ResultClient, write_file
from .base import BaseHandler


class UploadView(BaseHandler):
    """Request handler handling the upload form."""

    def get(self):
        """
        Answer to GET requests.

        Show the upload form.
        Renders `upload.html`
        """
        cookie = self.get_cookie()
        self.render("upload.html", page_title="Upload", msgs=None, cookie=cookie)

    def post(self):
        """
        Answer to POST requests.

        The method that the rubberband UI calls to upload files.
        Renders `upload.html` containing log messages about upload.
        """
        paths = []
        files = self.request.files.get("resultFiles")
        expirationdate = self.get_argument("expirationdate", None)
        tags = self.get_argument("tags", [])
        if tags != []:
            tags = tags.split(",")
            tags = list(map(str.strip, tags))

        # write all files to local directory
        for f in files:
            paths.append(write_file(f["filename"], f["body"]))

        paths = tuple(paths)

        # ResultClient helps us process the uploaded files
        c = ResultClient(user=self.get_current_user())
        results = c.process_files(paths, tags=tags, expirationdate=expirationdate)
        msgs = results.getMessages()
        url = results.getUrl()
        if url:
            url = self.application.base_url + url

        # send a message to the user describing the results of the upload
        self.render("upload.html", page_title="Upload", msgs=msgs, resulturl=url)
