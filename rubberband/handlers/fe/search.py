from rubberband.models import TestSet
from rubberband.utils import get_uniques
from rubberband.handlers.common import search
from .base import BaseHandler


class SearchView(BaseHandler):
    def get(self):
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

        query = {}
        all_fields = additional_fields + query_fields
        for f in all_fields:
            value = self.get_query_argument(f, default=None)
            if value:
                query[f] = value
        options = get_options(query_fields)

        results = search(query)
        self.render("search_form.html", page_title="Search", search_options=options,
                results=results)


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
