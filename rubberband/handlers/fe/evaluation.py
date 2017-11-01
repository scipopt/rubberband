from datetime import datetime
from lxml import html

from .base import BaseHandler
from rubberband.constants import IPET_EVALUATIONS, FORMAT_DATETIME_SHORT
from rubberband.models import TestSet

from ipet import Experiment, TestRun
from ipet.evaluation import IPETEvaluation
import pandas as pd

import json
import string


class EvaluationView(BaseHandler):

    def get(self, eval_id):
        letters = list(string.ascii_uppercase)

        # get evalfile
        evalfile = IPET_EVALUATIONS[int(eval_id)]

        # read testrunids
        testrunids = self.get_argument("testruns").split(",")

        # read defaultgroup
        default = self.get_argument("default", testrunids[0])
        default_rbid = None

        # get testruns and setup ipet experiment
        ex = Experiment()
        testruns = []
        for i in testrunids:
            testruns.append(TestSet.get(id=i))

        if len(testrunids) > 26:
            letters = [x + y for x in letters for y in letters]

        testruns.sort(key=lambda x: x.git_commit_timestamp)

        count = 0
        repres = {}
        results = []
        for t in testruns:
            if t.meta.id == default:
                default_rbid = t.id

            results.append(t)
            ts = ""
            if t.git_commit_timestamp:
                ts = "(" + datetime.strftime(t.git_commit_timestamp, FORMAT_DATETIME_SHORT) + ")"
            repres[t.id] = letters[count] + " " + t.settings_short_name + " " + ts
            count = count + 1

            ipettestrun = TestRun()
            ipettestrun.data = pd.DataFrame(t.get_data()).T
            ex.testruns.append(ipettestrun)

        # evaluate with ipet
        ev = IPETEvaluation.fromXMLFile(evalfile["path"])
        ev.set_defaultgroup(default_rbid)
        longtable, aggtable = ev.evaluate(ex)

        # postprocessing
        html_long = longtable.to_html(border=0,
                classes="ipet-long-table ipet-table data-table table-hover compact")
        html_agg = aggtable.to_html(border=0,
                classes="ipet-aggregated-table ipet-table data-table table-hover compact")

        tables = []
        for table in [html_long, html_agg]:
            # split rowspan cells from the tables to enable js datatable
            tree = html.fromstring(table)
            table_rows = [e for e in tree.iter() if e.tag == "tr" or e.tag == "th"]
            for row in table_rows:
                cellcount = 0
                for cell in row.iter():
                    rowspan = cell.get("rowspan")
                    if rowspan is not None:
                        del cell.attrib["rowspan"]
                        del cell.attrib["valign"]
                        nextrow = row
                        for i in range(int(rowspan) - 1):
                            nextrow = nextrow.getnext()
                            newcell = html.fromstring(html.tostring(cell))
                            nextrow.insert(cellcount - 1, newcell)
                    cellcount = cellcount + 1
            # render to string and make the dataTable fit the width
            table = html.tostring(tree).decode("utf-8").replace("class", "width=100% class")
            # replace ids and so on
            for k, v in repres.items():
                table = table.replace(k, v)
            tables.append(table)

        html_long = tables[0]
        html_agg = tables[1]

        # render to strings
        html_tables = self.render_string("results/evaluation.html",
                ipet_long_table=html_long,
                ipet_aggregated_table=html_agg).decode("utf-8")
        results_table = self.render_string("results_table.html",
                results=results, representation=repres, radios=True,
                checked=default,
                tablename="ipet-legend-table").decode("utf-8")

        # send evaluated data
        mydict = {"ipet-legend-table": results_table,
                "ipet-eval-result": html_tables}
        self.write(json.dumps(mydict))
