"""Contains DownloadView."""
from tornado.web import HTTPError
import zipfile
from io import BytesIO
import os

from rubberband.constants import IPET_EVALUATIONS, EXPORT_FILE_TYPES
from .base import BaseHandler
from .result import load_testsets


class DownloadView(BaseHandler):
    """Request handler handling the download of archives."""

    def get(self, arg):
        """
        Answer to GET requests.

        Pack everything into archive and send it for download.

        Parameters
        ----------
        arg : str
            "testsets=id1,id2,...,idn"

        Return archive.
        """
        testsets = self.get_argument("testsets", default="")
        evaluation = self.get_argument("evaluation", default="")

        if testsets != "" and evaluation == "":
            ts_ids = testsets.split(",")
            ts_list = load_testsets(ts_ids)

            zipname = "rubberband_testsets.zip"
            with BytesIO() as byteio:

                with zipfile.ZipFile(byteio, "w", zipfile.ZIP_DEFLATED) as archive:
                    for ts in ts_list:
                        for ftype in EXPORT_FILE_TYPES:
                            try:
                                archive.writestr("{}/{}{}".format(ts.meta.id,
                                    os.path.splitext(ts.filename)[0], ftype), ts.raw(ftype))
                            except TypeError:
                                pass

                self.set_header('Content-Type', 'application/zip')
                self.set_header("Content-Disposition", "attachment; filename=%s" % zipname)
                self.write(byteio.getvalue())
            self.finish()
        elif evaluation != "" and testsets == "":
            try:
                evalfile = IPET_EVALUATIONS[int(evaluation)]["path"]
            except:
                raise HTTPError(404)

            evalfilename = os.path.basename(evalfile)

            buf_size = 1024
            self.set_header('Content-Type', 'text/plain')
            self.set_header("Content-Disposition", "attachment; filename=%s" % evalfilename)

            with open(evalfile, 'r') as f:
                while True:
                    data = f.read(buf_size)
                    if not data:
                        break
                    self.write(data)
            self.finish()
        else:
            raise HTTPError(404)
