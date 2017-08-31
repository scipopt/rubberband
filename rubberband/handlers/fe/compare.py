from .base import BaseHandler
from rubberband.models import TestSet
from rubberband.handlers.fe.search import get_options


class CompareView(BaseHandler):
    def get(self):
        '''
        this is the ordinary view
        '''
        options = get_options()

        base_id = self.get_argument("base", None)
        base = TestSet.get(id=base_id)
        options["defaults"] = {}
        # preselect base testset
        options["defaults"]["test_set"] = base.test_set

        rrt = self.render_string("results_table.html", results=[base], checkboxes=False)
        rrt = rrt.decode("utf-8").replace('id="results-table"','id="base"')
        self.render("compare.html", page_title="Compare", base=base,
                search_options=options, rendered_results_table=rrt)

    def post(self):
        '''
        post requests for compareview, receives selection of instances to comparison
        '''
        # compares contains the meta ids (the hashes?) of all but one comparison TestSet
        compares = list(self.request.arguments.keys())
        base = self.get_argument("base", None)
        if base is not None and len(compares) == 1:
            self.write_error(400, msg="Please select at least 1 Testrun to compare to.")
            return
        elif base is None and len(compares) <= 1:
            self.write_error(400, msg="Please select at least 2 Testruns to compare.")
            return
        # base identifies via meta id (via hash?) one of the comparison TestSet
        if base:
            compares.remove("base")
            if base in compares:
                compares.remove(base)
        else:
            base = compares.pop(0)

        cmp_string = ",".join(compares)
        next_url = "{}/result/{}?compare={}".format(self.application.base_url, base, cmp_string)
        self.redirect(next_url)
