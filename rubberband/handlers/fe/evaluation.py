"""Contains EvaluationView."""
from lxml import html
import pandas as pd

import json
import logging

from .base import BaseHandler
from rubberband.constants import IPET_EVALUATIONS, NONE_DISPLAY, ALL_SOLU
from rubberband.models import TestSet
from rubberband.utils import RBLogHandler
from rubberband.utils.helpers import get_rbid_representation, setup_testruns_subst_dict

from ipet import Experiment, TestRun
from ipet.evaluation import IPETEvaluation


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
        else it writes ipet-long-table and ipet-aggregated-table into a json dict
        """
        # default and implicit style is ipetevaluation. if given latex, generate a table in the
        # style of the release report
        style = self.get_argument("style", None)

        # setup logger
        if style is None:

            ipetlogger = logging.getLogger("ipet")
            rbhandler = RBLogHandler(self)

            rbhandler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            rbhandler.setFormatter(formatter)

            ipetlogger.addHandler(rbhandler)

        # get evalfile
        evalfile = IPET_EVALUATIONS[int(eval_id)]
        if style is not None and style == "latex":
            evalfile = '''<?xml version="1.0" ?>
<!-- group by githash - exclude fails & aborts -->
<Evaluation comparecolformat="%.3f" index="ProblemName Seed Permutation Settings LPSolver GitHash" indexsplit="3">
    <Column formatstr="%.2f" name="T" origcolname="SolvingTime" minval="0.5"
        comp="quot shift. by 1" maxval="TimeLimit" alternative="TimeLimit"
        reduction="shmean shift. by 1">
        <Aggregation aggregation="shmean" name="sgm" shiftby="1.0"/>
    </Column>
    <Column formatstr="%.0f" name="N" origcolname="Nodes" comp="quot shift. by 100"
        reduction="shmean shift. by 100">
        <Aggregation aggregation="shmean" name="sgm" shiftby="100.0" />
    </Column>
    <FilterGroup name="\cleaninst">
        <Filter anytestrun="all" expression1="_abort_" expression2="0" operator="eq"/>
        <Filter anytestrun="all" expression1="_fail_" expression2="0" operator="eq"/>
    </FilterGroup>
    <FilterGroup active="True" filtertype="intersection" name="\\affected">
        <Filter anytestrun="all" expression1="_abort_" expression2="0" operator="eq"/>
        <Filter anytestrun="all" expression1="_fail_" expression2="0" operator="eq"/>
        <Filter active="True" anytestrun="one" datakey="LP_Iterations_dualLP" operator="diff"/>
        <Filter active="True" anytestrun="one" expression1="_solved_"
            expression2="1" operator="eq"/>
    </FilterGroup>
    <FilterGroup name="\\bracket{0}{tilim}">
        <Filter anytestrun="all" expression1="_abort_" expression2="0" operator="eq"/>
        <Filter anytestrun="all" expression1="_fail_" expression2="0" operator="eq"/>
        <Filter anytestrun="one" expression1="_solved_" expression2="1" operator="eq"/>
    </FilterGroup>
    <FilterGroup name="\\bracket{1}{tilim}">
        <Filter anytestrun="all" expression1="_abort_" expression2="0" operator="eq"/>
        <Filter anytestrun="all" expression1="_fail_" expression2="0" operator="eq"/>
        <Filter anytestrun="one" expression1="_solved_" expression2="1" operator="eq"/>
        <Filter anytestrun="one" expression1="T" expression2="1" operator="ge"/>
    </FilterGroup>
    <FilterGroup name="\\bracket{10}{tilim}">
        <Filter anytestrun="all" expression1="_abort_" expression2="0" operator="eq"/>
        <Filter anytestrun="all" expression1="_fail_" expression2="0" operator="eq"/>
        <Filter anytestrun="one" expression1="_solved_" expression2="1" operator="eq"/>
        <Filter anytestrun="one" expression1="T" expression2="10" operator="ge"/>
    </FilterGroup>
    <FilterGroup name="\\bracket{100}{tilim}">
        <Filter anytestrun="all" expression1="_abort_" expression2="0" operator="eq"/>
        <Filter anytestrun="all" expression1="_fail_" expression2="0" operator="eq"/>
        <Filter anytestrun="one" expression1="_solved_" expression2="1" operator="eq"/>
        <Filter anytestrun="one" expression1="T" expression2="100" operator="ge"/>
    </FilterGroup>
    <FilterGroup name="\\bracket{1000}{tilim}">
        <Filter anytestrun="all" expression1="_abort_" expression2="0" operator="eq"/>
        <Filter anytestrun="all" expression1="_fail_" expression2="0" operator="eq"/>
        <Filter anytestrun="one" expression1="_solved_" expression2="1" operator="eq"/>
        <Filter anytestrun="one" expression1="T" expression2="1000" operator="ge"/>
    </FilterGroup>
    <FilterGroup name="\\alloptimal">
        <Filter anytestrun="all" expression1="_abort_" expression2="0" operator="eq"/>
        <Filter anytestrun="all" expression1="_fail_" expression2="0" operator="eq"/>
        <Filter anytestrun="all" expression1="_solved_" expression2="1" operator="eq"/>
    </FilterGroup>
    <FilterGroup name="\difftimeouts">
        <Filter anytestrun="all" expression1="_abort_" expression2="0" operator="eq"/>
        <Filter anytestrun="all" expression1="_fail_" expression2="0" operator="eq"/>
        <Filter anytestrun="one" expression1="_solved_" expression2="1" operator="eq"/>
        <Filter anytestrun="one" expression1="_solved_" expression2="0" operator="eq"/>
    </FilterGroup>
    <FilterGroup active="True" filtertype="intersection" name="\miplib~2017">
        <Filter anytestrun="all" expression1="_abort_" expression2="0" operator="eq"/>
        <Filter anytestrun="all" expression1="_fail_" expression2="0" operator="eq"/>
        <Filter active="True" anytestrun="all" datakey="ProblemName" operator="keep">
            <Value active="True" name="MIPLIB2017"/>
        </Filter>
    </FilterGroup>
    <FilterGroup active="True" filtertype="intersection" name="\miplib~2010">
        <Filter anytestrun="all" expression1="_abort_" expression2="0" operator="eq"/>
        <Filter anytestrun="all" expression1="_fail_" expression2="0" operator="eq"/>
        <Filter active="True" anytestrun="all" datakey="ProblemName" operator="keep">
            <Value active="True" name="MIPLIB2010"/>
        </Filter>
    </FilterGroup>
    <FilterGroup active="True" filtertype="intersection" name="\coral">
        <Filter anytestrun="all" expression1="_abort_" expression2="0" operator="eq"/>
        <Filter anytestrun="all" expression1="_fail_" expression2="0" operator="eq"/>
        <Filter active="True" anytestrun="one" datakey="ProblemName" operator="keep">
            <Value active="True" name="COR@L"/>
        </Filter>
    </FilterGroup>
    <FilterGroup active="True" filtertype="intersection" name="continuous">
        <Filter anytestrun="all" expression1="_abort_" expression2="0" operator="eq"/>
        <Filter anytestrun="all" expression1="_fail_" expression2="0" operator="eq"/>
        <Filter anytestrun="all" expression1="PresolvedProblem_ContVars"
            expression2="PresolvedProblem_Vars" operator="eq"/>
    </FilterGroup>
    <FilterGroup active="True" filtertype="intersection" name="integer">
        <Filter anytestrun="all" expression1="_abort_" expression2="0" operator="eq"/>
        <Filter anytestrun="all" expression1="_fail_" expression2="0" operator="eq"/>
        <Filter anytestrun="all" expression1="PresolvedProblem_ContVars"
            expression2="PresolvedProblem_Vars" operator="lt"/>
    </FilterGroup>
</Evaluation>
'''

        tolerance = self.get_argument("tolerance")
        if tolerance == "":
            tolerance = 1e-6

        # read testrunids
        testrun_ids = self.get_argument("testruns")
        testrunids = testrun_ids.split(",")

        # read defaultgroup
        default_id = self.get_argument("default", testrunids[0])

        # get testruns and default
        testruns = get_testruns(testrunids)

        # evaluate with ipet
        ex = setup_experiment(testruns)
        ev = setup_evaluation(evalfile, ALL_SOLU, tolerance,
                evalstring=(style is not None and style == "latex"))

        # set defaultgroup
        set_defaultgroup(ev, ex, default_id)

        # do evaluation
        longtable, aggtable = ev.evaluate(ex)

        # None style is default
        if style is None:

            # add filtergroup buttons to ipet long table
            fg_buttons_str, longtable["Filtergroups"] = generate_filtergroup_selector(longtable, ev)

            # get substitutions dictionary
            repres = setup_testruns_subst_dict(testruns)

            cols_dict = get_columns_dict(longtable, {**repres["short"], **repres["all"]})

            # add id column to longtable
            longtable.insert(0, "id", range(1, len(longtable) + 1))
            delcols = [i for i in longtable.columns if i[-1] == "groupTags"]
            longtable = longtable.drop(delcols, axis=1)

            # convert to html and get style
            add_classes = " ".join([self.rb_dt_borderless, self.rb_dt_compact])  # style for table
            html_long = table_to_html(longtable, ev, html_id="ipet-long-table",
                    add_class=add_classes)
            html_agg = table_to_html(aggtable, ev, html_id="ipet-aggregated-table",
                    add_class=add_classes)

            ipetlogger.removeHandler(rbhandler)
            rbhandler.close()

            # postprocessing
            html_long = process_ipet_table(html_long, {**repres["short"], **repres["all"]},
                    add_ind=False, swap=True)
            html_agg = process_ipet_table(html_agg, {**repres["long"], **repres["all"]},
                    add_ind=True, swap=False)

            # render to strings
            html_tables = self.render_string("results/evaluation.html",
                    ipet_long_table=html_long,
                    ipet_aggregated_table=html_agg,
                    columns=cols_dict).decode("utf-8")

            # send evaluated data
            mydict = {"rb-ipet-eval-result": html_tables,
                      "rb-ipet-buttons": fg_buttons_str}
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

            cols = [c for c in df.columns if (c in ['Group', colindex, '_solved_'] or c.
                startswith("N_") or c.startswith("T_")) and not c.endswith(")p")]

            cols1 = [c for c in cols if c.endswith("Q") or c in ['Group', colindex]]
            cols2 = [c for c in cols if not c.endswith("Q") or c in ['Group', colindex]]
            df_rel = df[cols1]
            df_abs = df[cols2]
            df_count = df["_count_"]

            # groups in rows
            rows = ['\cleaninst', '\\affected', '\\bracket{0}{tilim}', '\\bracket{1}{tilim}',
                    '\\bracket{10}{tilim}', '\\bracket{100}{tilim}',
                    '\\bracket{1000}{tilim}', '\difftimeouts', '\\alloptimal',
                    '\miplibs', '\coral', 'continuous', 'integer']

            df_rel = df_rel.pivot_table(index=['Group'], columns=[colindex]).swaplevel(
                    axis=1).sort_index(axis=1, level=0, sort_remaining=True, ascending=False)
            df_abs = df_abs.pivot_table(index=['Group'], columns=[colindex]).swaplevel(
                    axis=1).sort_index(axis=1, level=0, sort_remaining=True, ascending=False)
            df_count = df.pivot_table(values=['_count_'], index=['Group'],
                    columns=[colindex]).swaplevel(axis=1)

            df = df_abs
            df.insert(loc=0, column=('NaN', "instances"), value=df_count[df_count.columns[0]])
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

            # split lines into a list
            latex_list = out.splitlines()
            # insert a `\midrule` at third last position in list (which will be the fourth last
            # line in latex output)
            latex_list.insert(14, '\cmidrule{1-10}')
            latex_list.insert(7, '\cmidrule{1-10}')
            latex_list.insert(3, '\cmidrule{3-5} \cmidrule{6-8} \cmidrule{9-10}')
            # join split lines to get the modified latex output string
            out = '\n'.join(latex_list)

            # postprocessing
            repl = get_replacement_dict(cols, colindex)
            for t in testruns:
                repl[t.get_data(colindex)] = t.get_data("ReportVersion")
            for k, v in repl.items():
                out = out.replace(k, v)

            tridstr = ",".join([tr for tr in testrunids if tr != default_id])
            baseurl = self.get_rb_base_url()
            evaluation_url = "{}/result/{}?compare={}#evaluation".format(baseurl,
                    default_id, tridstr)
            out = insert_into_latex(out, evaluation_url)

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
    latex_table_top = r"""
% table automatically generated by rubberband, please have a look and check everything
\begin{table}
\caption{Performance comparison}
\label{tbl:rubberband_table}
\scriptsize

"""
    latex_table_bottom = r"""
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
            repl[" " + i + " "] = "        nodes "
        if i.startswith("T_"):
            repl[" " + i + " "] = "       time "
    repl["_solved_"] = "  solved"
    repl["Group"] = "Subset               "
    repl["NaN"] = "  -"
    repl["nan"] = "  -"
    repl["timeQ"] = "time"
    repl["nodesQ"] = "nodes"
    repl["{} & instances"] = "Subset                & instances"
    repl[colindex + " &"] = "&"
    repl["egin{tabular"] = r"egin{tabular*}{\textwidth"
    repl["end{tabular"] = "end{tabular*"
    repl[r'- & \multi'] = r"  & \multi"
    return repl


def setup_experiment(testruns):
    """
    Setup an ipet experiment for the given testruns.

    Parameters
    ----------
    testruns : list
        a list of rubberband TestSet

    Returns
    -------
    ipet.experiment
        experiment
    """
    ex = Experiment()
    ex.addSoluFile(ALL_SOLU)

    # get data
    for t in testruns:
        # update representation
        additional_data = {"RubberbandId": get_rbid_representation(t, "extended")}

        # collect data and pass to ipet
        ipettestrun = TestRun()
        tr_raw_data = t.get_data(add_data=additional_data)
        ipettestrun.data = pd.DataFrame(tr_raw_data).T

        ex.testruns.append(ipettestrun)
    return ex


def process_ipet_table(table, repres, add_ind=False, swap=False):
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
    swap : bool
        Swap the first two rows of header

    Returns
    -------
    str
        The html table as a string.
    """
    # split rowspan cells from the tables body to enable js datatable
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
    htmltable = replace_in_str(htmltable, repres)
    htmltable = htmltable.replace("nan", NONE_DISPLAY)
    return htmltable


def replace_in_str(rstring, repres):
    """Replace keys by values of repres in rstring."""
    for k in sorted(repres.keys(), key=len, reverse=True):
        rstring = rstring.replace(k, repres[k])
    return rstring


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


def table_to_html(df, ev, html_id="", add_class=""):
    """
    Convert an ipet table to an html table.

    Parameters
    ----------
    df : pandas.dataframe
    ev : ipet.evaluation
    html_id : str

    Returns
    -------
    html
        html object of table
    """
    formatters = ev.getColumnFormatters(df)

    # apply sortlevel
    df = ev.sortDataFrame(df)

    tableclasses = 'ipet-table rb-table-data {}" width="100%'.format(add_class)

    htmlstr = df.to_html(border=0,
            na_rep=NONE_DISPLAY, formatters=formatters, justify="right",
            table_id=html_id, classes=tableclasses)

    return html.fromstring(htmlstr)


def get_testruns(testrunids):
    """
    Collect testruns from the ids.

    Parameters
    ----------
    testrunids : list or string
        list of testrun ids or a single one

    Returns
    -------
    list
        corresponding rubberband.TestSet(s)
    """
    if type(testrunids) is not list:
        return TestSet.get(id=testrunids)

    testruns = []
    for i in testrunids:
        t = TestSet.get(id=i)
        testruns.append(t)
    return testruns


def setup_evaluation(evalfile, solufile, tolerance, evalstring=False):
    """
    Setup the IPET evaluation.

    Parameters
    ----------
    evalfile : str
        name of evaluation file to use
    solufile : str
        name of solution file to use
    tolerance : str
        tolerance for validation
    evalstring : bool
        evalfile a string (or a filename)

    Returns
    -------
    ipet.IPETEvaluation
    """
    if evalstring:
        evaluation = IPETEvaluation.fromXML(evalfile)
    else:
        evaluation = IPETEvaluation.fromXMLFile(evalfile["path"])

    evaluation.set_grouptags(True)
    evaluation.set_validate(solufile)
    evaluation.set_feastol(tolerance)
    return evaluation


def set_defaultgroup(evaluation, experiment, testrun_id):
    """
    Set defaultgroup implied by testrun_id based on evaluation.

    Parameters
    ----------
    evaluation : ipet.IPETEvaluation
        evaluation to use
    experiment : ipet.IPETExperiment
        experiment to use
    testrun_id : str
        testrun setting defaultgroup
    """
    index = evaluation.getColIndex()
    # testrun_id can be found in column "RubberbandMetaId"
    df = experiment.getJoinedData()[index + ["RubberbandMetaId"]]
    df = df[df.RubberbandMetaId == testrun_id]
    defaultgroup_list = list(df.iloc[0][index])
    defaultgroup_string = ":".join(defaultgroup_list)
    evaluation.set_defaultgroup(defaultgroup_string)


def generate_filtergroup_selector(table, evaluation):
    """
    Generate a string with html filtergroup selector for ipet long table and and a column for table.

    Parameters
    ----------
    table : pandas.DataFrame
        ipet long table
    evaluation : ipet.IPETEvaluation
        corresponding ipet evaluation

    Returns
    -------
    str, pandas.Series
        selector and additional column
    """
    table = table.copy()
    gtindex = [c for c in table.columns if c[-1] == "groupTags"][0]
    table["Filtergroups"] = list(map("|{}|".format, table[gtindex]))

    out = '<div id="ipet-long-table-filter col"><label class="col-form-label text-left">Select filtergroups:<select id="ipet-long-filter-select" class="custom-select">' # noqa

    for fg in evaluation.getActiveFilterGroups():
        fg_name = fg.getName()
        fg_data = evaluation.getInstanceGroupData(fg)

        # don't show empty filtergroups
        if len(fg_data) == 0:
            continue

        # construct new option string
        newoption = '<option value="' + fg_name + '">' + fg_name + '</option>' # noqa

        # update selector strin
        out = out + newoption

    maxfgstr = ",".join(["|{}|".format(fg.getName()) for fg in evaluation.getActiveFilterGroups()])
    maxlen = len(maxfgstr)

    pd.set_option('max_colwidth', max(pd.get_option('display.max_colwidth'), maxlen))
    out = out + '</select></label></div>'
    return out, table["Filtergroups"]


def get_columns_dict(table, replace):
    """Construct a dictionary with column headers and ids, also replace given by replace dict."""
    # 0 is name, 1 is id
    if type(table.index) == pd.MultiIndex:
        colcount = 1 + len(table.index[0])
    else:
        colcount = 2
    cols = {}
    for c in table.columns:
        c_repres = ",".join(c)
        if "Filtergroups" not in c:
            cols[colcount] = replace_in_str(str(c_repres), replace)
        colcount = colcount + 1
    return cols
