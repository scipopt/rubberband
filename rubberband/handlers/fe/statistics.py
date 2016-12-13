from tornado.web import HTTPError

from .base import BaseHandler
from rubberband.models import TestSet


class StatisticsView(BaseHandler):
    def get(self, parent_id):
        compare = self.get_query_argument("compare", default="")
        print(compare)

        data = TestSet.get(id=parent_id)
        if not data:
            raise HTTPError(404)

        compare_values = compare.split(",")
        compare = []
        for c in compare_values:
            compare.append(TestSet.get(id=c))

        # get statistics if query params present
        if self.get_query_argument("field1", default=None) is not None:
            i = 1
            search = []
            while self.get_query_argument("field" + str(i), default=None):
                components = {}
                components["field"] = self.get_query_argument("field" + str(i))
                components["comparator"] = self.get_query_argument("comparator" + str(i))
                components["value"] = self.get_query_argument("value" + str(i))
                search.append(components)
                i += 1

            instances = find_matching(data, search)

            if instances:
                data.load_stats(subset=instances)
                data.matched = instances

        self.render("statistics.html", page_title="Custom Statistics", file=data, compare=compare)


def find_matching(TestSetObj, search):
    '''
    Find instances that match the search criteria.
    '''
    matching = []
    TestSetObj.load_children()
    for c in TestSetObj.children:
        evaluated_expressions = []
        for component in search:
            v = getattr(TestSetObj.children[c], component["field"], None)
            if v is not None:
                expression = str(v) + component["comparator"] + component["value"]
                evaluated_expressions.append(eval(expression))
        # all expressions evaluated to True
        if evaluated_expressions and all(evaluated_expressions):
            matching.append(c)
    return matching
