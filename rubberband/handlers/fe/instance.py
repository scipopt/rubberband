import json
import logging
from elasticsearch_dsl import A

from rubberband.models import TestSet, Result
from .base import BaseHandler


class InstanceView(BaseHandler):
    '''
    Single instance view
    '''
    def get(self, parent_id, child_id):
        r = Result.get(id=child_id, routing=parent_id)
        count = Result.search().filter("term", instance_name=r.instance_name).count()

        compare = self.get_argument("compare", default=[])
        if compare:
            compare_ids = compare.split(",")
            compare = load_results(compare_ids, r.instance_name)

        self.render("instance_detail_view.html", result=r, num_results=count, compare=compare,
                    page_title="Instance Result")


class InstanceNamesEndpoint(BaseHandler):
    def get(self):
        '''
        Get a list of all instance names in Elasticsearch.
        Used for `visualize` tab instance search typeahead.
        '''
        s = Result.search()
        a = A("terms", field="instance_name", size=0)  # set size to 0 so all results are returned
        s.aggs.bucket("unique_instances", a)
        s = s.params(search_type="count")
        res = s.execute()

        names = [x["key"] for x in res.aggregations["unique_instances"]["buckets"]]
        logging.info("Found {} distinct instance names.".format(len(names)))

        return self.write(json.dumps(names))


class InstanceEndpoint(BaseHandler):
    def get(self, parent_id):
        '''
        Return a Result with all instances attached.
        '''
        res = TestSet.get(id=parent_id)
        return self.write(res.json())


def load_results(parent_ids, name):
    '''
    Load the instance results from the various parents.
    '''
    results = []

    for id in parent_ids:
        f = TestSet.get(id=id)
        f.load_children()
        results.append(f.children[name])

    return results
