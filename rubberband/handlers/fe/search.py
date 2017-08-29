from rubberband.models import TestSet
from rubberband.utils import get_uniques
from rubberband.handlers.common import search
from .base import BaseHandler


class SearchView(BaseHandler):
    def get(self):
        # this is the ordinary view
        query = {}
        qf, af = get_query_fields()
        options = get_options(qf)

        results = search(query)
        self.render("search_form.html", page_title="Search", search_options=options, results=results)

    def post(self):
        # this is the ajax backend that provides the table of results
        qf, af = get_query_fields()
        query = self.fill_query(qf + af)
        options = get_options(qf)

        results = search(query)
        self.render("search_form.html", page_title="Search", search_options=options,
                results=results)

    def fill_query(self, all_fields):
        query = {}
        for f in all_fields:
            value = self.get_query_argument(f, default=None)
            if value:
                query[f] = value
        return query

def get_query_fields():
    query_fields = [
        "test_set",
        "mode",
        "run_initiator",
        "settings_short_name",
        "solver",
        "solver_version",
        "lp_solver",
        "lp_solver_version",
    ]
    additional_fields = [
        "git_hash",
        "tags",
    ]
    return query_fields, additional_fields

def get_options(fields):
    options = {}
    for field in fields:
        values = get_uniques(TestSet, field)
        # version sorting
        if field.endswith("_version"):
            values.sort(reverse=True)
        else:
            values.sort()

        options[field] = values

    return options
