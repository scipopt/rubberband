"""Contains EvaluationView."""
from datetime import datetime
from lxml import html

from .base import BaseHandler
from rubberband.constants import IPET_EVALUATIONS, FORMAT_DATETIME_SHORT, \
        NONE_DISPLAY
from rubberband.models import TestSet

from ipet import Experiment, TestRun
from ipet.evaluation import IPETEvaluation
import pandas as pd

import json
import string


class EvaluationView(BaseHandler):
    """Request handler caring about the evaluation of sets of TestRuns."""

    def get(self, eval_id):
        """
        Answer to GET requests.

        Evaluate TestRuns with IPET, read id of evaluation file from URL.

        Parameters
        ----------
        eval_id : str
            id of evaluation file read from url by routes.

        Writes latex version of ipet-agg-table via file.html if style option in url is `latex`,
        else it writes ipet-long-table and ipet-agg-table as json
        """
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
        ex, results, repres, default_rbid = setup_experiment(testruns, default_rbid)
        ev = IPETEvaluation.fromXMLFile(evalfile["path"])
        ev.set_defaultgroup(default_rbid)
        longtable, aggtable = ev.evaluate(ex)
        longtable["Filtergroups"] = "all"
        filtergroupbuttons = 'Show filtergroups: <div id="ipet-long-filter-buttons"'
        filtergroupbuttons = filtergroupbuttons + 'class="btn-group" role="group">'
        for fg in ev.getActiveFilterGroups():
            longtable["Newfiltergroup"] = ""
            fgname = fg.getName()
            fgdf = ev.getInstanceGroupData(fg)
            if fgname == "all":
                continue
            if len(fgdf) == 0:
                continue
            newbutton = '<button id="ipet-long-filter-button" type="button"'
            newbutton = newbutton + 'class="btn btn-sm btn-info">' + fgname + '</button>'
            fgdf["Newfiltergroup"] = fgname
            longtable.update(fgdf)
            newcolumn = longtable[["Filtergroups", "Newfiltergroup"]].apply(
                lambda x: x[0] if pd.isnull(x[1]) else ''.join(x), axis=1)
            longtable["Filtergroups"] = newcolumn
            filtergroupbuttons = filtergroupbuttons + newbutton
        longtable.drop(columns=["Newfiltergroup"], inplace=True)
        filtergroupbuttons = filtergroupbuttons + '</div>'

        # None style is default
        if style is None:
            filtergroupdata = {}
            for fg in ev.getActiveFilterGroups():
                filtergroupdata[fg] = ev.getInstanceGroupData(fg)

            # postprocessing
            longtable.insert(0, "id", range(1, len(longtable) + 1))
            html_long, style_long = table_to_html(longtable, ev, add_class="ipet-long-table")
            html_agg, style_agg = table_to_html(aggtable, ev, add_class="ipet-aggregated-table")

            html_long = process_ipet_table(html_long, repres["short"], add_ind=False) + \
                html.tostring(style_long).decode("utf-8")
            html_agg = process_ipet_table(html_agg, repres["long"], add_ind=True) + \
                html.tostring(style_agg).decode("utf-8")

            # render to strings
            html_tables = self.render_string("results/evaluation.html",
                    ipet_long_table=html_long,
                    ipet_aggregated_table=html_agg).decode("utf-8")

            results_table = self.render_string("results_table.html",
                    results=results, representation=repres["template"], radios=True,
                    checked=default,
                    tablename="ipet-legend-table").decode("utf-8")

            # send evaluated data
            mydict = {"ipet-legend-table": results_table,
                    "ipet-eval-result": html_tables,
                    "buttons": filtergroupbuttons}
            self.write(json.dumps(mydict))
        elif style == "latex":
            # generate a table that can be used in the release-report
            df = aggtable
            # care for the columns
            df = df.reset_index()
            poss = ['RubberbandId', 'GitHash', 'Settings', 'LPSolver']
            for i in poss:
                if i in df.columns:
                    colindex = i

            cols = [c for c in df.columns if (c in ['Group', colindex, '_time_'] or
                c.startswith("N_") or c.startswith("T_")) and not c.endswith(")p")]

            cols1 = [c for c in cols if c.endswith("Q") or c in ['Group', colindex]]
            cols2 = [c for c in cols if not c.endswith("Q") or c in ['Group', colindex]]
            df_rel = df[cols1]
            df_abs = df[cols2]
            df_count = df["_count_"]

            # groups in rows
            rows = ['clean', '[0,tilim]', '[1,tilim]', '[10,tilim]', '[100,tilim]', '[1000,tilim]',
                    'diff-timeouts', 'MMM compl (387)', 'Cor@l (349)', 'continuous', 'integer']

            df_rel = df_rel.pivot_table(index=['Group'], columns=[colindex]).swaplevel(
                    axis=1).sort_index(axis=1, level=0, sort_remaining=True, ascending=False)
            df_abs = df_abs.pivot_table(index=['Group'], columns=[colindex]).swaplevel(
                    axis=1).sort_index(axis=1, level=0, sort_remaining=True, ascending=False)
            df_count = df.pivot_table(values=['_count_'], index=['Group'],
                    columns=[colindex]).swaplevel(axis=1)

            df = df_abs
            df.insert(loc=0, column=(None, "instances"), value=df_count[df_count.columns[0]])
            for key in df_abs.columns:
                df[key] = df_abs[key]
            for key in df_rel.columns:
                if not df_rel[key].mean() == 1.0:
                    (a, b) = key
                    df['relative', b] = df_rel[key]

            df = df.loc[df.index.intersection(rows)].reindex(rows)

            # render to latex
            formatters = get_column_formatters(df)
            out = df.to_latex(column_format='@{}l@{\\;\\;\\extracolsep{\\fill}}rrrrrrrrr@{}',
                    multicolumn_format="c", escape=False, formatters=formatters)

            # postprocessing
            repl = get_replacement_dict(cols, colindex)
            for t in testruns:
                repl[t.get_data(colindex)] = t.get_data("ReportVersion")
            for k, v in repl.items():
                out = out.replace(k, v)

            out = insert_into_latex(out, self.get_rb_url())

            # send reply
            self.render("file.html", contents=out)


def get_column_formatters(df):
    """
    Get the formatters for a dataframe.

    Parameters
    ----------
    df : pandas dataframe
        table

    Returns
    -------
    dict
        dictionary of formatters for columns.
    """
    formatters = {}
    for p in df.columns:
        (a, b) = p
        if b.endswith("Q"):
            formatters[p] = lambda x: "%.2f" % x
        elif b.startswith("T_"):
            formatters[p] = lambda x: "%.1f" % x
        else:
            formatters[p] = lambda x: "%.0f" % x
    return formatters


def insert_into_latex(body, url):
    """
    Surround a latex table body by a latex header and footer.

    Add a comment with link to url.

    Parameters
    ----------
    body : str
        latex table body
    url : str
        url to current page

    Returns
    -------
    str
        the complete latex table
    """
    latex_table_top = """
% table automatically generated by rubberband, please have a look and check everything
\\begin{table}
\label{tbl:rubberband_table}
\caption{Performance comparison}
\scriptsize

"""
    latex_table_bottom = """
\end{table}

"""
    return latex_table_top + body + latex_table_bottom + "%% " + url


def get_replacement_dict(cols, colindex):
    """
    Get the replacement dict for latex representation.

    Parameters
    ----------
    cols : columns
        columns of table
    colindex : key
        title of additional column

    Returns
    -------
    dict
        replacement dictionary as `key` -> `value` pairs
    """
    # collect keys for replacement
    repl = {}
    for i in cols:
        if i.startswith("N_"):
            repl[" " + i + " "] = " nodes "
        if i.startswith("T_"):
            repl[" " + i + " "] = " time "
    repl["_time_"] = "timeout"
    repl["Group"] = "Subset"
    repl["NaN"] = "  -"
    repl["nan"] = "  -"
    repl["relative} \\\\\n"] = """relative} \\\\
\\cmidrule{3-5} \cmidrule{6-8} \cmidrule{9-10}\n"""
    repl["timeQ"] = "time"
    repl["nodesQ"] = "nodes"
    repl["{} & instances"] = "Subset & instances"
    repl[colindex + " &"] = "&"
    repl["egin{tabular"] = "egin{tabular*}{\\textwidth"
    repl["end{tabular"] = "end{tabular*"
    repl["clean"] = "\\cleaninst"
    repl['[0,tilim]'] = "\\cmidrule{1-10}\n\\bracket{0}{tilim}"
    repl['[1,tilim]'] = "\\bracket{1}{tilim}"
    repl['[10,tilim]'] = "\\bracket{10}{tilim}"
    repl['[100,tilim]'] = "\\bracket{100}{tilim}"
    repl['[1000,tilim]'] = "\\bracket{1000}{tilim}"
    repl['diff-timeouts'] = "\\difftimeouts"
    repl['MMM compl (387)'] = "\\cmidrule{1-10}\n\\miplibs       "
    repl['Cor@l (349)'] = "\\coral     "
    repl['- & \multi'] = "  & \multi"
    return repl


def setup_experiment(testruns, default_rbid):
    """
    Setup an ipet experiment for the given testruns.

    Parameters
    ----------
    testrun : list
        a list of rubberband TestSet

    Return
    ipet.experiment, list, dict
        experiment,
        list of used TestSets
        dictionary of representation key value pairs
    """
    # evaluate with ipet
    letters = get_letters(len(testruns))

    ex = Experiment()
    repres = {"long": {}, "short": {}, "template": {}}
    results = []
    # get data
    for t in testruns:
        # collect result
        results.append(t)

        # update representation
        ts = ""
        ts_sort = ""
        if t.git_commit_timestamp:
            ts = "(" + datetime.strftime(t.git_commit_timestamp, FORMAT_DATETIME_SHORT) + ")"
            ts_sort = datetime.strftime(t.git_commit_timestamp, "%Y%m%d%H%M%S")
        extended_rbid = ts_sort + t.settings_short_name + t.id
        if t.id == default_rbid:
            default_rbid = extended_rbid

        repres["template"][extended_rbid] = t.id
        repres["long"][extended_rbid] = " " + t.settings_short_name + " " + ts

        # collect data and pass to ipet
        ipettestrun = TestRun()
        additional_data = {"RubberbandId": extended_rbid}
        ipettestrun.data = pd.DataFrame(
                t.get_data(add_data=additional_data)).T
        ex.testruns.append(ipettestrun)

    count = 0
    # sort substitution keys for testruns
    for extended_rbid in sorted(repres["template"].keys()):
        tid = repres["template"][extended_rbid]
        longname = letters[count] + repres["long"][extended_rbid]
        repres["short"][extended_rbid] = letters[count]
        repres["long"][extended_rbid] = longname
        # for template
        repres["template"][tid] = longname
        count = count + 1
    return ex, results, repres, default_rbid


def process_ipet_table(table, repres, add_ind=False):
    """
    Make some modifications to the html structure.

    Split all multirow cells and replace keys of repres by their corresponding values.

    Parameters
    ----------
    table : html
        html structure of table
    repres : dict
        Replacement dictionary, `key` -> `value`
    add_ind : bool
        Add indices to rows

    Returns
    -------
    str
        The html table as a string.
    """
    # split rowspan cells from the tables to enable js datatable
    table_rows = [e for e in table.find(".//tbody").iter() if e.tag == "tr" or e.tag == "th"]
    groupcount = 1
    oldtext = ""
    for row in table_rows:
        cellcount = 0
        for cell in row.iter():
            if add_ind and cellcount == 1 and cell.tag == "th" and cell.text != oldtext:
                cell.text = "{:0>2d}. {}".format(groupcount, cell.text)
                oldtext = cell.text
                groupcount = groupcount + 1
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
    """
    Construct an alphabetical list of letters.

    Parameters
    ----------
    quantity : int
        length of requested list, maximum length is 26^2.

    Returns
    -------
    list

    Example
    -------
    >>> 3
    ['A', 'B', 'C']
    >>> 29
    ['AA', 'AB', ... , 'AZ', 'BA', 'BB']
    """
    letters = list(string.ascii_uppercase)
    if quantity > 26:
        letters = [x + y for x in letters for y in letters]
    return letters


def highlight_series(s):
    """
    Highlight a series or datafragme with background color light gray.

    An apply function for pandas styler.
    Maps Series/DataFrame -> Series/Dataframe of identical

    Parameters
    ----------
    s : pandas Series or Dataframe

    Returns
    -------
    str
        css text-align attribute in form of s.
    """
    return ['background-color: #eee' for v in s]


def align_elems(s):
    """
    Align numbers to the right, everything else to the left.

    An applymap function for pandas styler.
    Maps scalar -> scalarstring with CSS "value: attribute" pair.

    Parameters
    ----------
    s : scalars in a pandas DataFrame

    Returns
    -------
    str
        css text-align attribute
    """
    align = 'right' if (type(s) is int or type(s) is float) else 'left'
    return 'text-align: %s' % align


def table_to_html(df, ev, add_class="", border=0):
    """
    Convert an ipet table to an html table, also gives a style.

    Parameters
    ----------
    df : pandas.dataframe
    ev : ipet.evaluation
    add_class : str
    border : int

    Returns
    -------
    html, style
        html object of table and corresponding style.
    """
    formatters = ev.getColumnFormatters(df)

    l = 0
    if isinstance(df.columns[0], tuple):
        l = len(df.columns[0]) - 1

    if l == 0:
        highlight_cols = [c for c in df.columns
                if (c.startswith("_") and c.endswith("_")) or c.endswith("Q")]
        p_cols = [c for c in df.columns if c.endswith(")p")]
    else:
        highlight_cols = [c for c in df.columns
                if (c[l].startswith("_") and c[l].endswith("_")) or c[l].endswith("Q")]
        p_cols = [c for c in df.columns if c[l].endswith(")p")]
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
