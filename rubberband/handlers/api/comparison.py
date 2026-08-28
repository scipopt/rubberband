"""Contains EvaluationView."""

from datetime import datetime

from ipet.evaluation import IPETEvaluation
from tornado.web import HTTPError

from rubberband.constants import FORMAT_DATE
from rubberband.handlers.fe.evaluation import (
    get_testruns,
    set_defaultgroup,
    setup_experiment,
)
from rubberband.utils import ALL_SOLU

from .base import BaseHandler, authenticated


class ComparisonEndpoint(BaseHandler):
    """Request handler caring about the comparison of sets of TestRuns."""

    @authenticated
    def get(self, base_id):
        """
        Answer to GET requests.

        Parameters
        ----------
        base_id
            ID of the base TestSet

        Compare TestRuns with IPET
        """
        if not base_id:
            raise HTTPError(404)

        # read testrunids
        comparison_ids = self.get_argument("compare", None)
        if comparison_ids is not None:
            testrunids = list(set(comparison_ids.split(",")))
            if base_id in testrunids:
                raise HTTPError(404)

        # get testruns and default
        baserun = get_testruns(base_id)
        testruns = []
        if comparison_ids is not None:
            testruns = get_testruns(testrunids)

        # timestamps
        basehash = baserun.git_hash
        times = {
            t.git_hash: datetime.strftime(t.git_commit_timestamp, FORMAT_DATE)
            for t in testruns + [baserun]
        }
        hashes = set([t.git_hash for t in testruns + [baserun]])
        if len(hashes) > 2:
            raise HTTPError(404)
        hashes.remove(basehash)

        comparehash = None
        if len(hashes) == 1:
            comparehash = hashes.pop()
            committime = times[comparehash]
        else:  # len(hashes) == 0:
            committime = times[basehash]

        # tolerance
        tolerance = float(self.get_argument("tolerance", default=1e-6))
        if tolerance == "":
            tolerance = 1e-6

        # evaluate with ipet
        ex, _ = setup_experiment(testruns + [baserun], "")
        evalstring = f"""<?xml version="1.0" ?>
<Evaluation comparecolformat="%.3f" index="ProblemName Seed Permutation GitHash" indexsplit="-1" fillin="True">
    <Column formatstr="%.2f" name="T" origcolname="SolvingTime" minval="0.5" comp="quot shift. by 1" maxval="TimeLimit" alternative="TimeLimit" reduction="shmean shift. by 1">
        <Aggregation aggregation="shmean" name="sgm" shiftby="1.0"/>
    </Column>
    <Column formatstr="%.2f" name="NrmT" origcolname="NormalizedTime" minval="0.5" comp="quot shift. by 1" maxval="TimeLimit" alternative="TimeLimit" reduction="shmean shift. by 1">
        <Aggregation aggregation="shmean" name="sgm" shiftby="1.0"/>
    </Column>
    <Column formatstr="%.0f" name="N" origcolname="Nodes" comp="quot shift. by 100" reduction="shmean shift. by 100">
        <Aggregation aggregation="shmean" name="sgm" shiftby="100.0" />
    </Column>
    <Column formatstr="%.2f" origcolname="TimeLimit" alternative="{baserun.time_limit}"
        reduction="mean">
    </Column>
    <FilterGroup name="all"/>
    <FilterGroup name="clean">
        <Filter anytestrun="all" expression1="_abort_" expression2="0" operator="eq"/>
        <Filter anytestrun="all" expression1="_fail_" expression2="0" operator="eq"/>
    </FilterGroup>
    <FilterGroup name="affected" filtertype="intersection">
        <Filter anytestrun="all" expression1="_abort_" expression2="0" operator="eq"/>
        <Filter anytestrun="all" expression1="_fail_" expression2="0" operator="eq"/>
        <Filter active="True" anytestrun="one" datakey="LP_Iterations_dualLP" operator="diff"/>
        <Filter active="True" anytestrun="one" expression1="_solved_" expression2="1" operator="eq"/>
    </FilterGroup>
    <FilterGroup name="all-optimal">
        <Filter anytestrun="all" expression1="_abort_" expression2="0" operator="eq"/>
        <Filter anytestrun="all" expression1="_fail_" expression2="0" operator="eq"/>
        <Filter anytestrun="all" expression1="_solved_" expression2="1" operator="eq"/>
    </FilterGroup>
</Evaluation>
        """
        ev = IPETEvaluation.fromXML(evalstring)
        if ALL_SOLU:
            ev.set_validate(ALL_SOLU)
        ev.set_feastol(tolerance)

        set_defaultgroup(ev, ex, base_id)

        # do evaluation
        longtable, aggtable = ev.evaluate(ex)

        # df = aggtable[["_count_","_solved_","T_sgm(1.0)Q","T_sgm(1.0)"]]

        if comparehash is not None:
            cleanindex = ("clean", comparehash)
            allindex = ("all", comparehash)
            alloptindex = ("all-optimal", comparehash)
            affindex = ("affected", comparehash)
            commithash = comparehash
        else:
            cleanindex = ("clean", basehash)
            allindex = ("all", basehash)
            alloptindex = ("all-optimal", basehash)
            affindex = ("affected", basehash)
            commithash = basehash

        allcount = aggtable["_count_"][allindex]
        allsolved = aggtable["_solved_"][allindex]
        alltime = aggtable["T_sgm(1.0)"][allindex]
        allnrmtime = aggtable["NrmT_sgm(1.0)"][allindex]
        allnodes = aggtable["N_sgm(100.0)"][allindex]
        cleancount = aggtable["_count_"][cleanindex]
        cleansolved = aggtable["_solved_"][cleanindex]
        cleantime = aggtable["T_sgm(1.0)"][cleanindex]
        cleannrmtime = aggtable["NrmT_sgm(1.0)"][cleanindex]
        cleannodes = aggtable["N_sgm(100.0)"][cleanindex]
        if alloptindex in aggtable["_count_"] :
            alloptcount = aggtable["_count_"][alloptindex]
            allopttime = aggtable["T_sgm(1.0)"][alloptindex]
            alloptnrmtime = aggtable["NrmT_sgm(1.0)"][alloptindex]
            alloptnodes = aggtable["N_sgm(100.0)"][alloptindex]
        else :
            alloptcount = 0
            allopttime = 0.0
            alloptnrmtime = 0.0
            alloptnodes = 0
        if affindex in aggtable["_count_"] :
            affcount = aggtable["_count_"][affindex]
            affsolved = aggtable["_solved_"][affindex]
            afftime = aggtable["T_sgm(1.0)"][affindex]
            affnrmtime = aggtable["NrmT_sgm(1.0)"][affindex]
            affnodes = aggtable["N_sgm(100.0)"][affindex]
        else :
            affcount = 0
            affsolved = 0
            afftime = 0.0
            affnrmtime = 0.0
            affnodes = 0


        # if we did not evaluate base only, then include also the numbers for base
        if comparehash is not None:
            basecleanindex = ("clean", basehash)
            baseallindex = ("all", basehash)
            basealloptindex = ("all-optimal", basehash)
            baseaffindex = ("affected", basehash)
            basecommithash = basehash
            basecommittime = times[basehash]
            baseallcount = aggtable["_count_"][baseallindex]
            baseallsolved = aggtable["_solved_"][baseallindex]
            basealltime = aggtable["T_sgm(1.0)"][baseallindex]
            baseallnrmtime = aggtable["NrmT_sgm(1.0)"][baseallindex]
            baseallnodes = aggtable["N_sgm(100.0)"][baseallindex]
            basecleancount = aggtable["_count_"][basecleanindex]
            basecleansolved = aggtable["_solved_"][basecleanindex]
            basecleantime = aggtable["T_sgm(1.0)"][basecleanindex]
            basecleannrmtime = aggtable["NrmT_sgm(1.0)"][basecleanindex]
            basecleannodes = aggtable["N_sgm(100.0)"][basecleanindex]
            if basealloptindex in aggtable["_count_"] :
                basealloptcount = aggtable["_count_"][basealloptindex]
                baseallopttime = aggtable["T_sgm(1.0)"][basealloptindex]
                basealloptnrmtime = aggtable["NrmT_sgm(1.0)"][basealloptindex]
                basealloptnodes  = aggtable["N_sgm(100.0)"][basealloptindex]
            else :
                basealloptcount = 0
                baseallopttime = 0.0
                basealloptnrmtime = 0.0
                basealloptnodes = 0
            if baseaffindex in aggtable["_count_"] :
                baseaffcount = aggtable["_count_"][baseaffindex]
                baseaffsolved = aggtable["_solved_"][baseaffindex]
                baseafftime = aggtable["T_sgm(1.0)"][baseaffindex]
                baseaffnrmtime = aggtable["NrmT_sgm(1.0)"][baseaffindex]
                baseaffnodes  = aggtable["N_sgm(100.0)"][baseaffindex]
            else :
                baseaffcount = 0
                baseaffsolved = 0
                baseafftime = 0.0
                baseaffnrmtime = 0.0
                baseaffnodes = 0
        else:
            basecommithash = 0
            basecommittime = 0
            baseallcount = 0
            baseallsolved = 0
            basealltime = 0
            baseallnrmtime = 0
            baseallnodes = 0
            basecleancount = 0
            basecleansolved = 0
            basecleantime = 0
            basecleannrmtime = 0
            basecleannodes = 0
            basealloptcount = 0
            baseallopttime = 0
            basealloptnrmtime = 0
            basealloptnodes = 0
            baseaffcount = 0
            baseaffsolved = 0
            baseafftime = 0
            baseaffnrmtime = 0
            baseaffnodes = 0

        self.write(
            ",".join(
                list(
                    map(
                        str,
                        [
                            commithash,
                            committime,
                            allcount,
                            allsolved,
                            alltime,
                            allnrmtime,
                            allnodes,
                            cleancount,
                            cleansolved,
                            cleantime,
                            cleannrmtime,
                            cleannodes,
                            alloptcount,
                            allopttime,
                            alloptnrmtime,
                            alloptnodes,
                            affcount,
                            affsolved,
                            afftime,
                            affnrmtime,
                            affnodes,
                            basecommithash,
                            basecommittime,
                            baseallcount,
                            baseallsolved,
                            basealltime,
                            baseallnrmtime,
                            baseallnodes,
                            basecleancount,
                            basecleansolved,
                            basecleantime,
                            basecleannrmtime,
                            basecleannodes,
                            basealloptcount,
                            baseallopttime,
                            basealloptnrmtime,
                            basealloptnodes,
                            baseaffcount,
                            baseaffsolved,
                            baseafftime,
                            baseaffnrmtime,
                            baseaffnodes
                        ],
                    )
                )
            )
        )

    def check_xsrf_cookie(self):
        """Turn off the xsrf cookie for upload api endpoint, since we check the user differently."""
