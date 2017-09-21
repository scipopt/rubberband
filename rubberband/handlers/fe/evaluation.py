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
                "Apple", "Banana", "Cherry", "Dragonfruit",
                "Elderberry", "Fig", "Grape", "Honey",
                "Ingwer", "Jackfruit", "Kiwi", "Lemon",
                "Mango", "Nectarine", "Orange", "Peach",
                "Quinoa", "Raspberry", "Strawberry", "Turnip",
                "U", "V", "Wasabi",
                "X", "Yuzu", "Zeno"]

        # get evalfile
        evalfile = IPET_EVALUATIONS[int(eval_id)]

        # get testruns and setup ipet experiment
        ex = Experiment()
        mapping = {}
        testrunids = self.get_argument("testruns").split(",")
        count = 0
        for i in testrunids:
            t = TestSet.get(id=i)
            mapping[t.filename] = representation[count]
            ipettestrun = TestRun()
            ipettestrun.data = pd.DataFrame(t.get_data()).T
            ex.testruns.append(ipettestrun)
            count = count + 1

        # evaluate with ipet
        ev = IPETEvaluation.fromXMLFile(evalfile["path"])
        table, aggregation = ev.evaluate(ex)

        # postprocessing
        legend = "<table class=\"stats-table table table-bordered\"><tr>\n"
        legend = legend + "<thead><th colspan=2>Legend of columnheadings</th></thead>\n"
        for k, f in mapping.items():
            legend = legend + "<tr><td>" + str(f) + "</td><td>" + k + "</td></tr>\n"
        legend = legend + "</tr></table>\n"

        htmltable = table.to_html(classes="stats-table table table-bordered")
        htmlagg = aggregation.to_html(classes="stats-table table table-bordered")
        htmltables = htmltable + htmlagg
        for k, f in mapping.items():
            htmltables = htmltables.replace(k, str(f))

        # send evaluated data
        self.write(legend + htmltables)
