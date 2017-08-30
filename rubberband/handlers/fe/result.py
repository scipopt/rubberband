from tornado.web import HTTPError
import logging

from .base import BaseHandler
from rubberband.models import TestSet


class ResultView(BaseHandler):
    '''
    Results view
    '''
    def get(self, parent_id):
        # parent id is the first argument: meta id of TestSet
        if not parent_id:
            raise HTTPError(404)
        parent = TestSet.get(id=parent_id, ignore=404)

        if not parent:
            raise HTTPError(404)

        # get data associated with TestSet, save in parent.children[]
        parent.load_children()

        compare = self.get_argument("compare", default=[])

        if compare:
            compare_ids = compare.split(",")
            compare = load_testsets(compare_ids)
            for c in compare:
                c.load_children()

            all_runs = [parent] + compare
            same_status = get_same_status(all_runs)
            parent.load_stats(same_status)
            for c in compare:
                c.load_stats(same_status)
            # save intersection results and difference results
            sets = get_intersection_difference([c.children.to_dict().keys() for c in all_runs])
        else:
            sets = {}
            # save stats in parent.stats
            parent.load_stats()

        metas = [key for md in [parent] + compare for key in md.to_dict().get('metadata', [])]
        meta = list(set(metas))
        meta.sort()

        rrt = self.render_string("results_table.html", results=[parent] + compare, checkboxes=False)
        self.render("result_view.html", file=parent, page_title="Result", compare=compare,
                    sets=sets, meta=meta, rendered_results_table=rrt)

    def post(self, parent_id):
        pass

    def put(self, parent_id):
        pass

    def delete(self, parent_id):
        '''
        Delete the TestSet and all associated results in Elasticsearch and Gitlab.
        '''
        user = self.get_current_user()

        # remove from db
        t = TestSet.get(id=parent_id)
        t.delete_all_associations()
        t.delete()

        msg = "{} deleted {}".format(user, t.meta.id)
        logging.info(msg)


def load_testsets(ids):
    tss = []
    for id in ids:
        t = TestSet.get(id=id)
        t.load_children()
        tss.append(t)

    return tss


def get_same_status(runs):
    instances = runs[0].children.to_dict()
    final_instances = set([])
    for i in instances:
        statuses = []
        for r in runs:
            rd = r.children.to_dict()
            if i in rd:
                statuses.append(rd[i]["Status"])

        if len(statuses) == len(runs) and len(set(statuses)) == 1:
            final_instances.add(i)

    return final_instances


def get_intersection_difference(runs):
    '''
    Get the intersection and difference of the list of lists.
    '''
    intersection = set(runs[0])
    difference = set()

    for r in runs:
        intersection = intersection & r
        difference.update(r)

    difference -= intersection

    return {
                "intersection": intersection,
                "difference": difference,
            }
