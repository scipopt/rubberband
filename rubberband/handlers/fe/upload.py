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
        self.render("upload.html", page_title="Upload", msgs=[])

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

        paths = tuple(paths)
        messages = []
        bundles = bundle_files(paths)
        for bundle in bundles:
            # ResultClient helps us process the uploaded files
            c = ResultClient(user=self.get_current_user())
            results = c.process_files(bundle, tags=tags, expirationdate=expirationdate)
            msgs = results.getMessages()
            url = results.getUrl()
            if url:
                url = self.application.base_url + url
            messages.append([msgs, url])

        # send a message to the user describing the results of the upload
        self.render("upload.html", page_title="Upload", msgs=messages)


def bundle_files(paths):
    """Take a bundle of files and split them by basename."""
    bundles = []
    for f in [path for path in paths if path[-4:] == ".out"]:
        basename = f[:-4]
        bundles.append([path for path in paths if path[:-4] == basename])
    for f in paths:
        if f[-5:] == ".solu":
            for bundle in bundles:
                if f not in bundle:
                    bundle.append(f)
    print(bundles)
    return bundles
