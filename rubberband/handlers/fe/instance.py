"""Contains InstanceView."""

import json
from elasticsearch.dsl import A

from rubberband.models import TestSet, Result
from .base import BaseHandler


class InstanceView(BaseHandler):
    """Request handler handling requests for a single instance."""

    def get(self, result_id):
        """
        Answer to GET requests.

        Get information about a single Instance, as a Result.

        Parameters
        ----------
        result_id : str
            id of Result

        Renders `instance_detail_view.html`.
        """
        r = Result.get(id=result_id)
        count = Result.search().filter("term", instance_name=r.instance_name).count()

        compare = self.get_argument("compare", default=[])
        if compare:
            compare_ids = compare.split(",")
            compare = load_results(compare_ids, r.instance_name)

        self.render(
            "instance_detail_view.html",
            result=r,
            num_results=count,
            compare=compare,
            page_title="Instance Result",
        )


class InstanceNamesEndpoint(BaseHandler):
    """Get names of instances."""

    def get(self):
        """
        Answer to GET requests.

        Used for `visualize` tab instance search typeahead.

        Write a list of all instance names in Elasticsearch.
        """
        s = Result.search()
        a = A("terms", field="instance_name")
        s.aggs.bucket("unique_instances", a)
        res = s.execute()
        names = [x["key"] for x in res.aggregations["unique_instances"]["buckets"]]

        return self.write(json.dumps(names))


class InstanceEndpoint(BaseHandler):
    """Access information about instances."""

    def get(self, testset_id):
        """
        Answer to GET requests.

        Parameters
        ----------
        testset_id : str
            Id of TestSet

        Write a Result with all instances attached.
        """
        res = TestSet.get(id=testset_id)
        return self.write(res.json())


def load_results(testset_ids, name):
    """
    Load the instance results from the various TestSets.

    Parameters
    ----------
    testset_ids : str
        Ids of TestSets
    name : str
        Name of instance Result

    Returns
    -------
    list
        List of Results
    """
    results = []

    for id in testset_ids:
        f = TestSet.get(id=id)
        f.load_results()
        results.append(f.results[name])

    return results
