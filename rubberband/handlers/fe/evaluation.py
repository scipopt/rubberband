from datetime import datetime
from lxml import html

from .base import BaseHandler
from rubberband.constants import IPET_EVALUATIONS, FORMAT_DATETIME_SHORT, NONE_DISPLAY
from rubberband.models import TestSet

from ipet import Experiment, TestRun
from ipet.evaluation import IPETEvaluation
import pandas as pd

import json
import string


class EvaluationView(BaseHandler):

    def get(self, eval_id):
        # get evalfile
        evalfile = IPET_EVALUATIONS[int(eval_id)]

        # read testrunids
        testrunids = self.get_argument("testruns").split(",")

        # read defaultgroup
        default = self.get_argument("default", testrunids[0])
        default_rbid = None

        # get testruns
        testruns = []
        for i in testrunids:
            t = TestSet.get(id=i)
            if t.meta.id == default:
                default_rbid = t.id
            testruns.append(t)

        testruns.sort(key=lambda x: x.git_commit_timestamp)

        # evaluate with ipet
        ex, results, repres = setup_experiment(testruns)
        ev = IPETEvaluation.fromXMLFile(evalfile["path"])
        ev.set_defaultgroup(default_rbid)
        longtable, aggtable = ev.evaluate(ex)

        # postprocessing
        longtable.insert(0, "id", range(1, len(longtable) + 1))
        html_long, style_long = table_to_html(longtable, ev, add_class="ipet-long-table")
        html_agg, style_agg = table_to_html(aggtable, ev, add_class="ipet-aggregated-table")

        html_long = process_ipet_table(html_long, repres) + \
            html.tostring(style_long).decode("utf-8")
        html_agg = process_ipet_table(html_agg, repres) + \
            html.tostring(style_agg).decode("utf-8")

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


def setup_experiment(testruns):
    # evaluate with ipet
    letters = get_letters(len(testruns))

    ex = Experiment()
    count = 0
    repres = {}
    results = []
    # get data
    for t in testruns:
        # collect result
        results.append(t)

        # update representation
        ts = ""
        if t.git_commit_timestamp:
            ts = "(" + datetime.strftime(t.git_commit_timestamp, FORMAT_DATETIME_SHORT) + ")"
        repres[t.id] = letters[count] + " " + t.settings_short_name + " " + ts
        count = count + 1

        # collect data and pass to ipet
        ipettestrun = TestRun()
        ipettestrun.data = pd.DataFrame(t.get_data()).T
        ex.testruns.append(ipettestrun)

    return ex, results, repres


def process_ipet_table(table, repres):
    # split rowspan cells from the tables to enable js datatable
    table_rows = [e for e in table.find(".//tbody").iter() if e.tag == "tr" or e.tag == "th"]
    for row in table_rows:
        cellcount = 0
        for cell in row.iter():
            rowspan = cell.get("rowspan")
            if rowspan is not None:
                del cell.attrib["rowspan"]
                nextrow = row
                for i in range(int(rowspan) - 1):
                    nextrow = nextrow.getnext()
                    newcell = html.fromstring(html.tostring(cell))
                    nextrow.insert(cellcount - 1, newcell)
            cellcount = cellcount + 1

    # render to string and make the dataTable fit the width
    htmltable = html.tostring(table).decode("utf-8")
    # replace ids and so on
    for k, v in repres.items():
        htmltable = htmltable.replace(k, v)
    htmltable = htmltable.replace("nan", NONE_DISPLAY)
    return htmltable


def get_letters(quantity):
    letters = list(string.ascii_uppercase)
    if quantity > 26:
        letters = [x + y for x in letters for y in letters]
    return letters


# apply functions for pandas styler: Series/DataFrame -> Series/Dataframe of identical
# shape of strings with CSS "value: attribute" pair
def highlight_series(s):
    return ['background-color: #eee' for v in s]


# applymap functions for pandas styler: scalar -> scalarstring with CSS "value: attribute" pair
def align_elems(s):
    align = 'right' if (type(s) is int or type(s) is float) else 'left'
    return 'text-align: %s' % align


def table_to_html(df, ev, add_class="", border=0):
    formatters = ev.getColumnFormatters(df)
    l = 0
    if isinstance(df.columns[0], tuple):
        l = len(df.columns[0]) - 1

    if l == 0:
        highlight_cols = [c for c in df.columns
            if (c[l].startswith("_") and c[l].endswith("_")) or c[l].endswith("Q")]
    else:
        highlight_cols = [c for c in df.columns
            if (c[l].startswith("_") and c[l].endswith("_")) or c[l].endswith("Q")]
    # apply formatters styles
    styler = df.style.format(formatters).\
        applymap(align_elems)

    # style requires a nonempty subset
    if highlight_cols != []:
        styler = styler.apply(highlight_series, subset=highlight_cols)

    htmlstr = styler.render()
    tree = html.fromstring(htmlstr)
    treestyle = tree.find(".//style")
    treetable = tree.find(".//table")
    treetable.set("width", "100%")

    tableclasses = add_class + " ipet-table data-table compact"
    treetable.set("class", tableclasses)

    return treetable, treestyle
