from .base import BaseHandler
from rubberband.models import TestSet
from rubberband.handlers.fe.search import SearchView, get_options, get_query_fields
from rubberband.handlers.common import search
from elasticsearch_dsl import Search


class CompareView(BaseHandler):
    def get(self):
        # get requests for search
        qf, af = get_query_fields()
        query = SearchView.fill_query(self, qf + af)

        base_id = self.get_argument("base", None)
        base = TestSet.get(id=base_id)
        query["test_set"] = base.test_set

        options = get_options(qf)
        results = search(query)
        # don't include base in list
        results = [r for r in results if not r == base]

        self.render("compare.html", page_title="Compare", base=base,
                results=results, search_options=options)

    def post(self):
        # post requests for compareview
        # compares contains the meta ids (the hashes?) of all but one comparison TestSet
        compares = list(self.request.arguments.keys())
        # base identifies via meta id (via hash?) one of the comparison TestSet
        base = self.get_argument("base", None)
        if base:
            compares.remove("base")
            if base in compares:
                compares.remove(base)
        else:
            base = compares.pop(0)

        cmp_string = ",".join(compares)
        next_url = "{}/result/{}?compare={}".format(self.application.base_url, base, cmp_string)
        self.redirect(next_url)
