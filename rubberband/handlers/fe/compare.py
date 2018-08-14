"""Contains CompareView."""
from .base import BaseHandler
from rubberband.models import TestSet
from rubberband.handlers.fe.search import get_options
from tornado.web import HTTPError


class CompareView(BaseHandler):
    """Request handler caring about comparison of more than one TestRun."""

    def get(self):
        """
        Answer to GET requests.

        Redirects to search view.
        """
        self.redirect("search", status=301)

    def post(self):
        """
        Answer to POST requests.

        Gets called when the user clicks on "change comparison base".
        Organizes instances and constructs url.
        Redirects to CompareView.get().
        """
        # compares contains the meta ids of all TestSets that should be compared, base among these
        compares = list(self.request.arguments.keys())
        if "compare" in compares:
            compares.remove("compare")

        base = self.get_argument("base", None)
        if base is not None and len(compares) == 1:
            raise HTTPError(status_code=400, msg="Please select at least 1 Testrun to compare to.")
        elif base is None and len(compares) <= 1:
            raise HTTPError(status_code=400, log_message="Please select at least 2 Testruns to compare.")

        # base is identified via meta id as one of the comparison TestSets
        if base:
            compares.remove("base")
            if base in compares:
                compares.remove(base)
        else:
            base = compares.pop(0)

        cmp_string = ",".join(compares)
        next_url = "{}/result/{}?compare={}".format(self.application.base_url, base, cmp_string)
        self.redirect(next_url)
