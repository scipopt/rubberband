"""Contains UploadView."""

from rubberband.utils import Importer, write_file
from rubberband.utils.importer import bundle_files
from .base import BaseHandler


class UploadView(BaseHandler):
    """Request handler handling the upload form."""

    def get(self):
        """
        Answer to GET requests.

        Show the upload form.
        Renders `upload.html`
        """
        self.render("upload.html", page_title="Upload", infos=[])

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

        if files is None:
            self.redirect("/upload")
        # write all files to local directory
        for f in files:
            paths.append(write_file(f["filename"], f["body"]))

        infos = []
        bundles = bundle_files(paths)
        for bundle in bundles:
            # Importer helps us process the uploaded files
            c = Importer(user=self.current_user)
            importstats = c.process_files(
                bundle, tags=tags, expirationdate=expirationdate
            )

            info = {}
            info["messages"] = importstats.getMessages()
            url = importstats.getUrl()
            if url:
                url = self.application.base_url + url
            info["url"] = url

            infos.append(info)

        # send a message to the user describing the results of the upload
        self.render("upload.html", page_title="Upload", infos=infos)
