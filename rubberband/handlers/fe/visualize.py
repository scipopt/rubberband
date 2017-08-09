import datetime
from elasticsearch_dsl import Q
import json

from .base import BaseHandler
from rubberband.models import TestSet, Result


class VisualizeView(BaseHandler):

    def get(self):
        '''
        Show the form for the user to enter data that they want to visualize.
        '''
        # by default show results from the last year
        start_date = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime("%Y-%m-%d")
        end_date = datetime.datetime.now().strftime("%Y-%m-%d")
        # show the form to enter data
        self.render("visualize.html", page_title="Visualize", default_start_date=start_date,
                    default_end_date=end_date)

    def post(self):
        '''
        AJAX endpoint from frontend.
        Invoked after the user clicked on 'submit' in visualize-view
        '''
        query_type = self.get_argument('data-type', None)
        query = self.get_argument('data-name', None)
        start_date = self.get_argument('start-date', None)
        end_date = self.get_argument('end-date', None)

        if not all([query_type, query, start_date, end_date]):
            return self.write(json.dumps([]))

        final_data = []
        range_params = {
            "git_commit_timestamp": {
                "gte": start_date,
                "lte": end_date,
                "format": "date"
            }
        }

        if query_type == "Instance":
            s = Result.search()
            # Q is for Query
            s = s.filter(Q("has_parent", type="testset", query=Q("range", **range_params)))
            s = s.filter(Q("term", instance_name=query))

            res = []
            for hit in s.scan():
                res.append(hit)

            for r in res:
                parent_data = TestSet.get(id=r.meta.parent)
                components = r.to_dict()
                components.update(parent_data.to_dict())
                components["parent_id"] = r.meta.parent
                final_data.append(components)

        elif query_type == "Test Set":
            s = TestSet.search()
            s = s.filter("and", Q("range", **range_params))
            s = s.filter(Q("term", test_set=query))

            res = []
            for hit in s.scan():
                res.append(hit)

            final_data.append(res)

        return self.write(json.dumps(final_data, default=date_handler))


date_handler = lambda obj: (  # noqa
    obj.isoformat()
    if isinstance(obj, datetime.datetime) or isinstance(obj, datetime.date)
    else None
)
