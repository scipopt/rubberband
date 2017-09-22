from .base import BaseHandler
from rubberband.constants import IPET_EVALUATIONS
from rubberband.models import TestSet

from ipet import Experiment, TestRun
from ipet.evaluation import IPETEvaluation
import pandas as pd


class EvaluationView(BaseHandler):

    def get(self, eval_id):
        # dummydata
        # dataframe = pd.DataFrame(
        #         columns=['a', 'b', 'c'],
        #         index=[1, 2, 3],
        #         data=[[1, 2, 3], [4, 5, 6], [7, 8, 9]])
        representation = [
                "Apfel", "Birne", "Cherry", "Dragonfruit",
                "Elderberry", "Fig", "Grape", "Honey",
                "Ingwer", "Jackfruit", "Kiwi", "Lemon",
                "Mango", "Nectarine", "Orange", "Peach",
                "Quinoa", "Raspberry", "Strawberry", "Turnip",
                "Ugli", "V", "Wasabi",
                "X", "Yuzu", "Zeno"]

        # get evalfile
        evalfile = IPET_EVALUATIONS[int(eval_id)]

        # get testruns and setup ipet experiment
        ex = Experiment()
        mapping = []
        testrunids = self.get_argument("testruns").split(",")
        count = 0
        for i in testrunids:
            t = TestSet.get(id=i)
            if t.filename not in mapping:
                mapping.append(t.filename)
            ipettestrun = TestRun()
            ipettestrun.data = pd.DataFrame(t.get_data()).T
            ex.testruns.append(ipettestrun)
            count = count + 1

        # evaluate with ipet
        ev = IPETEvaluation.fromXMLFile(evalfile["path"])
        table, aggregation = ev.evaluate(ex)

        # postprocessing
        htmltable = table.to_html(classes="stats-table table table-bordered")
        htmlagg = aggregation.to_html(classes="stats-table table table-bordered")
        for k in range(len(mapping)):
            htmltable = htmltable.replace(mapping[k], representation[k])
            htmlagg = htmlagg.replace(mapping[k], representation[k])

        htmldata = self.render_string("results/ipet-evaluation.html",
                representation=representation,
                mapping=mapping,
                ipet_long_table=htmltable,
                ipet_aggregated_table=htmlagg)
        # send evaluated data
        self.write(htmldata)
