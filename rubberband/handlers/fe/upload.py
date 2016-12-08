from rubberband.utils import ResultClient, write_file
from .base import BaseHandler


class UploadView(BaseHandler):
    def get(self):
        cookie = self.get_cookie()
        self.render("upload.html", page_title="Upload", msgs=None, cookie=cookie)

    def post(self):
        '''
        The method that the rubberband UI calls to upload files.
        '''
        paths = []
        files = self.request.files.get("resultFiles")
        tags = self.get_argument("tags", [])
        if tags != []:
            tags = tags.split(",")
            tags = list(map(str.strip, tags))

        for f in files:
            paths.append(write_file(f["filename"], f["body"]))

        paths = tuple(paths)

        c = ResultClient(user=self.get_current_user())
        results = c.process_files(paths, tags=tags)
        msgs = results.getMessages()
        url = results.getUrl()
        if url:
            url = self.application.base_url + url

        # send a message to the user describing the results of the upload
        self.render("upload.html", page_title="Upload", msgs=msgs, resulturl=url)
