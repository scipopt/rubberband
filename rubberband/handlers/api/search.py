"""Contains Search api endpoint."""

import json

from rubberband.handlers.common import search
from rubberband.models import date_handler
from .base import BaseHandler, authenticated


class SearchEndpoint(BaseHandler):
    """Request handler handling the search."""

    @authenticated
    def get(self):
        """
        Answer to GET requests.

        The initial search view, possibly prefilled with query string options.
        """
        query_fields = [
            "test_set",
            "mode",
            "run_initiator",
            "settings_short_name",
            "solver",
            "solver_version",
            "lp_solver",
            "lp_solver_version",
            "git_hash",
            "tags",
        ]

        query = {}
        for f in query_fields:
            value = self.get_query_argument(f, default=None)
            if value:
                query[f] = value

        r = []
        if query:
            result = search(query)
            for h in result.hits:
                r.append(h.to_dict())

        response = json.dumps(r, default=date_handler)
        self.write(response)
