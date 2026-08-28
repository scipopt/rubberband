"""Contains VisualizeView."""

import datetime
import json

from elasticsearch.dsl import Q

from rubberband.constants import FORMAT_DATE
from rubberband.models import Result, TestSet

from .base import BaseHandler


class VisualizeView(BaseHandler):
    """Request handler caring about visualization of rubberband data."""

    def get(self):
        """
        Answer to GET requests.

        Show the form for the user to enter data that they want to visualize.
        Renders `visualize.html`.
        """
        # by default show results from the last year
        start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime(
            FORMAT_DATE
        )
        end_date = datetime.datetime.now().strftime(FORMAT_DATE)
        # show the form to enter data
        self.render(
            "visualize.html",
            page_title="Visualize",
            default_start_date=start_date,
            default_end_date=end_date,
        )

    def post(self):
        """
        Answer to POST requests.

        AJAX endpoint from frontend.
        Invoked after the user clicked on 'submit' in visualize-view.
        Write data as json.
        """
        query_type = self.get_argument("data-type", None)
        query = self.get_argument("data-name", None)
        start_date = self.get_argument("start-date", None)
        end_date = self.get_argument("end-date", None)

        if not all([query_type, query, start_date, end_date]):
            return self.write(json.dumps([]))

        final_data = []
        range_params = {
            "git_commit_timestamp": {
                "gte": start_date,
                "lte": end_date,
                "format": "date",
            }
        }

        if query_type == "Instance":
            s = Result.search()
            # Q is for Query
            s = s.filter(Q("term", instance_name=query))
            s = s.filter("range", **range_params)

            datakeys = {
                "file_path": "",
                "opt_flag": "opt",
                "Nodes": -1,
                "TotalTime_solving": -1,
                "Iterations": -1,
                "git_commit_timestamp": "",
                "Status": "unkn",
                "testset_id": "",
                "filename": "",
            }

            # this uses pagination/scroll
            for r in s.scan():
                testset = TestSet.get(id=r.testset_id)
                components = r.to_dict()
                components.update(testset.to_dict())
                components["testset_id"] = r.testset_id
                final_components = {
                    k: components.get(k, v) for k, v in datakeys.items()
                }
                final_data.append(final_components)

            # only need the following keys: ["git_commit_timestamp", "Nodes", "Status", "opt_flag",
            # "TotalTime_solving", "Iterations", "file_path", "testset_id", "filename"]:

        elif query_type == "Test Set":
            s = TestSet.search()
            s = s.filter("and", Q("range", **range_params))
            s = s.filter(Q("term", test_set=query))

            # this uses pagination/scroll
            res = [hit for hit in s.scan()]

            final_data.append(res)

        return self.write(json.dumps(final_data, default=date_handler))


date_handler = lambda obj: (
    obj.isoformat() if isinstance(obj, (datetime.datetime, datetime.date)) else None
)
