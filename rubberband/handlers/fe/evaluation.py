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

        # default and implicit style is ipetevaluation. if given latex, generate a table in the
        # style of the release report
        style = self.get_argument("style", None)

        # get testruns
        testruns = []
        for i in testrunids:
            t = TestSet.get(id=i)
            if t.meta.id == default:
                default_rbid = t.id
            testruns.append(t)

        try:
            testruns.sort(key=lambda x: x.git_commit_timestamp)
        except:
            pass

        # evaluate with ipet
        ex, results, repres = setup_experiment(testruns)
        ev = IPETEvaluation.fromXMLFile(evalfile["path"])
        ev.set_defaultgroup(default_rbid)
        longtable, aggtable = ev.evaluate(ex)

        # None style is default
        if style is None:
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
        elif style == "latex":
            # generate a table that can be used in the release-report
            df = aggtable
            # care for the columns
            df = df.reset_index()
            poss = ['GitHash', 'Settings', 'LPSolver']
            for i in poss:
                if i in df.columns:
                    colindex = i

            cols = [c for c in df.columns if (c in ['Group', colindex, '_time_'] or
                c.startswith("N_") or c.startswith("T_")) and not c.endswith(")p")]
            # collect keys for later replacement
            repl = {}
            repl["_time_"] = "timeout"
            for i in cols:
                if i.startswith("N_"):
                    repl[i] = "nodes"
                if i.startswith("T_"):
                    repl[i] = "time"

            cols1 = [c for c in cols if c.endswith("Q") or c in ['Group', colindex]]
            cols2 = [c for c in cols if not c.endswith("Q") or c in ['Group', colindex]]
            df_rel = df[cols1]
            df_abs = df[cols2]
            df_count = df["_count_"]

            # groups
            groups = ['[0,tilim]', '[1,tilim]', '[10,tilim]', '[100,tilim]', '[1000,tilim]',
                    'diff-timeouts']
            add_groups = ['MIPLIB2010 (87)', 'Cor@l (349)', 'continuous', 'integer']

            df_rel = df_rel.pivot_table(index=['Group'], columns=['GitHash']).swaplevel(
                    axis=1).sort_index(axis=1, level=0, sort_remaining=True, ascending=False)
            df_abs = df_abs.pivot_table(index=['Group'], columns=['GitHash']).swaplevel(
                    axis=1).sort_index(axis=1, level=0, sort_remaining=True, ascending=False)
            df_count = df.pivot_table(values=['_count_'], index=['Group'],
                    columns=['GitHash']).swaplevel(axis=1)

            df = df_abs
            df.insert(loc=0, column=(None, "instances"), value=df_count[df_count.columns[0]])
            for key in df_abs.columns:
                df[key] = df_abs[key]
            for key in df_rel.columns:
                if not df_rel[key].mean() == 1.0:
                    (a, b) = key
                    df['relative', b] = df_rel[key]

            rows = groups + add_groups
            df = df.loc[df.index.intersection(rows)].reindex(rows)

            # render to latex
            formatters = {}
            for p in df.columns:
                (a, b) = p
                if b.endswith("Q"):
                    formatters[p] = lambda x: "%.2f" % x
                elif b.startswith("T_"):
                    formatters[p] = lambda x: "%.1f" % x
                else:
                    formatters[p] = lambda x: "%.0f" % x
            out = df.to_latex(column_format='@{}l@{\\;\\;\\extracolsep{\\fill}}rrrrrrrrr@{}',
                    multicolumn_format="c", escape=False, formatters=formatters)

            # postprocessing
            repl["Group"] = "Subset"
            repl["NaN"] = "  -"
            repl["nan"] = "  -"
            repl["relative} \\\\\n"] = """relative} \\\\
\\cmidrule{3-5} \cmidrule{6-8} \cmidrule{9-10}\n"""
            repl["timeQ"] = "time"
            repl["nodesQ"] = "nodes"
            repl["{} & instances"] = "Subset & instances"
            repl["GitHash &         - &"] = "& &"
            repl["egin{tabular"] = "egin{tabular*}{\\textwidth"
            repl["end{tabular"] = "end{tabular*"
            repl['[0,tilim]'] = "\\bracket{0}{tilim}"
            repl['[1,tilim]'] = "\\bracket{1}{tilim}"
            repl['[10,tilim]'] = "\\bracket{10}{tilim}"
            repl['[100,tilim]'] = "\\bracket{100}{tilim}"
            repl['[1000,tilim]'] = "\\bracket{1000}{tilim}"
            repl['diff-timeouts'] = "\\difftimeouts"
            repl['MIPLIB2010 (87)'] = "\\cmidrule{1-10}\n\\miplib        "
            repl['Cor@l (349)'] = "\\coral     "
            for t in testruns:
                repl[t.get_data(colindex)] = t.get_data("ReportVersion")
            for k, v in repl.items():
                out = out.replace(k, v)

            latex_table_top = """
% table automatically generated by rubberband, please have a look and check everything
\\begin{table}
  \label{tbl:rubberband_table}
  \captin{Performance comparison}
  \scriptsize

  """
            latex_table_bottom = """
\end{table}

"""

            out = latex_table_top + out + latex_table_bottom + "%% " + self.get_rb_url()

            # send reply
            self.render("file.html", contents=out)


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
                if (c.startswith("_") and c.endswith("_")) or c.endswith("Q")]
        p_cols = [c for c in df.columns if c.endswith("p")]
    else:
        highlight_cols = [c for c in df.columns
                if (c[l].startswith("_") and c[l].endswith("_")) or c[l].endswith("Q")]
        p_cols = [c for c in df.columns if c[l].endswith("p")]
    for p in p_cols:
        formatters[p] = lambda x: "%.3f" % x
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
