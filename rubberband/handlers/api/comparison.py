"""Contains EvaluationView."""
from datetime import datetime
from tornado.web import HTTPError

from .base import BaseHandler, authenticated
from rubberband.constants import ALL_SOLU, FORMAT_DATE
from rubberband.handlers.fe.evaluation import setup_experiment, get_testruns, set_defaultgroup

from ipet.evaluation import IPETEvaluation


class ComparisonEndpoint(BaseHandler):
    """Request handler caring about the comparison of sets of TestRuns."""

    @authenticated
    def get(self, base_id):
        """
        Answer to GET requests.

        Parameters
        ----------
        parent_id
            Rubberband id of parent

        Compare TestRuns with IPET
        """
        if not base_id:
            raise HTTPError(404)

        # read testrunids
        testrun_ids = self.get_argument("compare")
        testrunids = testrun_ids.split(",")
        if base_id in testrunids:
            raise HTTPError(404)

        # get testruns and default
        baserun = get_testruns(base_id)
        testruns = get_testruns(testrunids)

        # timestamps
        basehash = baserun.git_hash
        times = {t.git_hash: datetime.strftime(t.git_commit_timestamp, FORMAT_DATE)
                for t in testruns}
        hashes = set([t.git_hash for t in testruns + [baserun]])
        if len(hashes) != 2:
            raise HTTPError(404)
        hashes.remove(basehash)

        comparehash = hashes.pop()
        comparetime = times[comparehash]

        # tolerance
        tolerance = float(self.get_argument("tolerance", default=1e-6))
        if tolerance == "":
            tolerance = 1e-6

        # evaluate with ipet
        ex = setup_experiment(testruns + [baserun])
        evalstring = """<?xml version="1.0" ?>
<Evaluation comparecolformat="%.3f" index="ProblemName GitHash" indexsplit="-1">
    <Column formatstr="%.2f" name="T" origcolname="SolvingTime" minval="0.5"
    comp="quot shift. by 1" maxval="TimeLimit" alternative="TimeLimit" reduction="mean">
        <Aggregation aggregation="shmean" name="sgm" shiftby="1.0"/>
    </Column>
    <FilterGroup name="clean">
        <Filter anytestrun="all" expression1="_abort_" expression2="0" operator="eq"/>
        <Filter anytestrun="all" expression1="_fail_" expression2="0" operator="eq"/>
    </FilterGroup>
</Evaluation>
        """
        ev = IPETEvaluation.fromXML(evalstring)
        ev.set_validate(ALL_SOLU)
        ev.set_feastol(tolerance)

        set_defaultgroup(ev, ex, base_id)

        # do evaluation
        _, aggtable = ev.evaluate(ex)

        # df = aggtable[["_count_","_solved_","T_sgm(1.0)Q","T_sgm(1.0)"]]

        compareindex = ("clean", comparehash)
        baseindex = ("clean", basehash)

        solved = aggtable["_solved_"][compareindex] / aggtable["_solved_"][baseindex]
        time = aggtable["T_sgm(1.0)Q"][compareindex]

        self.write(
                "\n".join([
                    aggtable.to_html(),
                    ",".join(list(map(str, [comparetime, solved, time])))
                    ])
                )

    def check_xsrf_cookie(self):
        """Turn off the xsrf cookie for upload api endpoint, since we check the user differently."""
        pass
