from .base import BaseHandler
from .result import load_testsets, get_same_status
from rubberband.models import TestSet


class StatisticsView(BaseHandler):
    def get(self, parent_id):
        base = TestSet.get(id=parent_id)

        compare = self.get_query_argument("compare", default=[])
        if compare:
            compare = compare.split(",")
            compare = load_testsets(compare)

        oneorall = self.get_query_argument("oneorall", default="all")
        testsets = [base] + compare
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

            instances_search = find_matching(testsets, search, oneorall)
            instances_statuses = get_same_status(testsets)
            instances_search &= instances_statuses

            if instances_search:
                for testset in testsets:
                    testset.load_stats(subset=instances_search)
                    testset.matched = instances_search

        rrt = self.render_string("results_table.html", results=[base] + compare)
        self.render("statistics.html", page_title="Custom Statistics", file=base, compare=compare,
                rendered_results_table=rrt)


def find_matching(TestSetObjs, search, oneorall):
    '''
    Find instances that match the search criteria.
    '''
    all_matching = set()
    for TestSetObj in TestSetObjs:
        matching = set([])
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
                matching.add(c)

        if not all_matching:  # seed all_matching
            all_matching = matching
        elif oneorall == "all":
            all_matching &= matching
        elif oneorall == "one":
            all_matching |= matching
        else:
            raise Exception("Unexpected value for oneorall: {}".format(oneorall))

    return all_matching
