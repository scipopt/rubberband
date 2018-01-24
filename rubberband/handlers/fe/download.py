"""Contains DownloadView."""
from tornado.web import HTTPError
import zipfile
from io import BytesIO

from rubberband.constants import EXPORT_FILE_TYPES
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
        if testsets is "":
            raise HTTPError(404)

        ts_ids = testsets.split(",")
        ts_list = load_testsets(ts_ids)

        zipname = "rubberband_testsets.zip"
        with BytesIO() as byteio:

            with zipfile.ZipFile(byteio, "w", zipfile.ZIP_DEFLATED) as archive:
                for ts in ts_list:
                    for ftype in EXPORT_FILE_TYPES:
                        try:
                            archive.writestr("{}/{}{}".format(ts.meta.id, ts.filename, ftype),
                                    ts.raw(ftype))
                        except TypeError:
                            pass

            self.set_header('Content-Type', 'application/zip')
            self.set_header("Content-Disposition", "attachment; filename=%s" % zipname)
            self.write(byteio.getvalue())
        self.finish()
