from rubberband.models import TestSet
from rubberband.utils import get_uniques
from rubberband.handlers.common import search
from .base import BaseHandler


class SearchView(BaseHandler):
    def get(self):
        '''
        this is the ordinary view
        '''
        options = get_options()

        self.render("search_form.html", page_title="Search", search_options=options)

    def post(self):
        '''
        this is the ajax backend that provides the table of results
        '''
        query = self.fill_query()
        results = search(query)
        exclude = self.get_argument("exclude_testset", default=None)
        if exclude:
            results = [r for r in results if r.meta.id != exclude]

        self.write(self.render_string("results_table.html", results=results, checkboxes=True))

    def fill_query(self, all_fields=None):
        if all_fields is None:
            all_fields = query_fields + additional_fields
        query = {}
        for f in all_fields:
            value = self.get_argument(f, default=None)
            if value:
                query[f] = value
        return query


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


def get_options(fields=None):
    if fields is None:
        fields = query_fields
    options = {}
    for field in fields:
        values, hot_values = get_uniques(TestSet, field)
        # version sorting
        if field.endswith("_version"):
            values.sort(reverse=True)
            hot_values.sort(reverse=True)
        else:
            values.sort()
            hot_values.sort()
        options[field] = []
        if len(hot_values) > 0:
            options[field] = hot_values + ["---------"]
        options[field].extend(values)
    options["defaults"] = {}
    return options
