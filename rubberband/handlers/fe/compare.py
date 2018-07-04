"""Contains CompareView."""
from .base import BaseHandler
from rubberband.models import TestSet
from rubberband.handlers.fe.search import get_options


class CompareView(BaseHandler):
    """Request handler caring about comparison of more than one TestRun."""

    def get(self):
        """
        Answer to GET requests.

        Renders `compare.html`.
        """
        options = get_options()

        base_id = self.get_argument("base", None)
        base = TestSet.get(id=base_id)

        compare_list = self.get_argument("compare", None)
        compares = []
        compareids = compare_list.split(",")
        for i in compareids:
            compares.append(TestSet.get(id=i))

        options["defaults"] = {}
        # preselect base testset
        options["defaults"]["test_set"] = base.test_set
        options["defaults"]["mode"] = base.mode

        rrt = self.render_string("results_table.html", results=[base]+compares, tablename="base")
        self.render("compare.html", page_title="Compare", base=base, compareids=compareids,
                search_options=options, rendered_results_table=rrt)

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
            self.write_error(400, msg="Please select at least 1 Testrun to compare to.")
            return
        elif base is None and len(compares) <= 1:
            self.write_error(400, msg="Please select at least 2 Testruns to compare.")
            return
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
