from .base import BaseHandler
from rubberband.constants import IPET_EVALUATIONS
from rubberband.models import TestSet

from ipet import Experiment, TestRun
from ipet.evaluation import IPETEvaluation
import pandas as pd

import json


class EvaluationView(BaseHandler):

    def get(self, eval_id):
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
        results = []
        repres = {}
        testrunids = self.get_argument("testruns").split(",")
        count = 0
        for i in testrunids:
            t = TestSet.get(id=i)

            results.append(t)
            repres[t.id] = representation[count]
            count = count + 1

            ipettestrun = TestRun()
            ipettestrun.data = pd.DataFrame(t.get_data()).T
            ex.testruns.append(ipettestrun)

        # evaluate with ipet
        ev = IPETEvaluation.fromXMLFile(evalfile["path"])
        table, aggregation = ev.evaluate(ex)

        # postprocessing
        htmltable = table.to_html(classes="stats-table table table-bordered")
        htmlagg = aggregation.to_html(classes="stats-table table table-bordered")

        for k, v in repres.items():
            htmltable = htmltable.replace(k, v)
            htmlagg = htmlagg.replace(k, v)

        htmldata = self.render_string("results/ipet-evaluation.html",
                ipet_long_table=htmltable,
                ipet_aggregated_table=htmlagg).decode("utf-8")

        resultstable = self.render_string("results_table.html",
                results=results, representation=repres,
                tablename="ipet-legend-table").decode("utf-8")

        # send evaluated data
        mydict = {"ipet-legend-table": resultstable,
                "ipet-eval-result": htmldata}
        self.write(json.dumps(mydict))
