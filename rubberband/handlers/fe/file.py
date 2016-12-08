from tornado.web import HTTPError

from rubberband.models import TestSet, Result
from rubberband.constants import EXPORT_DATA_FORMATS, EXPORT_FILE_TYPES
from .base import BaseHandler


class FileView(BaseHandler):
    '''
    View or download log files or log file contents.
    '''
    def get(self, file_id):
        instance_id = self.get_argument("instance", default=None)
        for_download = self.get_argument("download", default=False)
        fformat = self.get_argument("format", default="raw")
        ftype = self.get_argument("ftype", default=".out")

        # perform some validation on the query params
        if fformat not in EXPORT_DATA_FORMATS:
            raise HTTPError(404)

        if ftype not in EXPORT_FILE_TYPES:
            raise HTTPError(404)

        # load the appropriate object
        if instance_id:
            obj = Result.get(id=instance_id, routing=file_id)
        else:
            obj = TestSet.get(id=file_id)

        # e.g. `result.json(ftype=".set")`
        file_contents = getattr(obj, fformat)(ftype=ftype)

        if for_download:
            self.write(file_contents)
        else:
            self.render("file.html", contents=file_contents)
