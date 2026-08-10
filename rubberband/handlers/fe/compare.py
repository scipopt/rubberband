"""Contains CompareView."""

from .base import BaseHandler
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
        Redirects to CompareView.get(), or to AnalyzeExternalView when the
        LogAnalyzer button was used ("target" is "loganalyzer" then).
        """
        # compares contains the meta ids of all TestSets that should be compared, base among these
        compares = list(self.request.arguments.keys())
        if "_xsrf" in compares:
            compares.remove("_xsrf")
        if "compare" in compares:
            compares.remove("compare")

        # sent by the "Compare in LogAnalyzer" submit button only
        target = self.get_argument("target", None)
        if "target" in compares:
            compares.remove("target")

        base = self.get_argument("base", None)
        if base is not None and len(compares) == 1:
            raise HTTPError(
                status_code=400, msg="Please select at least 1 Testrun to compare to."
            )
        elif base is None and len(compares) <= 1:
            raise HTTPError(
                status_code=400,
                log_message="Please select at least 2 Testruns to compare.",
            )

        # base is identified via meta id as one of the comparison TestSets
        if base:
            compares.remove("base")
            if base in compares:
                compares.remove(base)
        else:
            base = compares.pop(0)

        if target == "loganalyzer":
            next_url = "{}/analyze/{}".format(
                self.application.base_url, ",".join([base] + compares)
            )
        else:
            next_url = "{}/result/{}?compare={}".format(
                self.application.base_url, base, ",".join(compares)
            )
        self.redirect(next_url)
