"""Contains EvaluationView."""
from lxml import html
import pandas as pd

import re
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
        # logging.info(msg="starting eval with uri".format(self.request.uri))
        style = self.get_argument("style", None)

        # setup logger
        if style is None:

            # ipetlogger = logging.getLogger("ipet")
            rbhandler = RBLogHandler(self)

            rbhandler.setLevel(logging.INFO)
            formatter = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
            rbhandler.setFormatter(formatter)

            # ipetlogger.addHandler(rbhandler)

        # get evalfile
        evalfile = IPET_EVALUATIONS[int(eval_id)]
        if style is not None and style == "latex":
            evalfile = '''<?xml version="1.0" ?>
<!-- group by githash - exclude fails & aborts -->
<Evaluation comparecolformat="%.3f" index="ProblemName Seed Permutation Settings LPSolver GitHash"
indexsplit="3">
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
     <FilterGroup active="True" filtertype="intersection" name="\\nonconvex">
        <Filter anytestrun="all" expression1="_abort_" expression2="0" operator="eq"/>
        <Filter anytestrun="all" expression1="_fail_" expression2="0" operator="eq"/>
        <Filter active="True" anytestrun="all" datakey="ProblemName" operator="keep">
            <Value active="True" name="4stufen"/>
            <Value active="True" name="alkyl"/>
            <Value active="True" name="alkylation"/>
            <Value active="True" name="arki0002"/>
            <Value active="True" name="arki0003"/>
            <Value active="True" name="arki0004"/>
            <Value active="True" name="arki0005"/>
            <Value active="True" name="arki0006"/>
            <Value active="True" name="arki0007"/>
            <Value active="True" name="arki0008"/>
            <Value active="True" name="arki0009"/>
            <Value active="True" name="arki0010"/>
            <Value active="True" name="arki0011"/>
            <Value active="True" name="arki0012"/>
            <Value active="True" name="arki0013"/>
            <Value active="True" name="arki0014"/>
            <Value active="True" name="arki0015"/>
            <Value active="True" name="arki0016"/>
            <Value active="True" name="arki0017"/>
            <Value active="True" name="arki0024"/>
            <Value active="True" name="autocorr_bern20-03"/>
            <Value active="True" name="autocorr_bern20-05"/>
            <Value active="True" name="autocorr_bern20-10"/>
            <Value active="True" name="autocorr_bern20-15"/>
            <Value active="True" name="autocorr_bern25-03"/>
            <Value active="True" name="autocorr_bern25-06"/>
            <Value active="True" name="autocorr_bern25-13"/>
            <Value active="True" name="autocorr_bern25-19"/>
            <Value active="True" name="autocorr_bern25-25"/>
            <Value active="True" name="autocorr_bern30-04"/>
            <Value active="True" name="autocorr_bern30-08"/>
            <Value active="True" name="autocorr_bern30-15"/>
            <Value active="True" name="autocorr_bern30-23"/>
            <Value active="True" name="autocorr_bern30-30"/>
            <Value active="True" name="autocorr_bern35-04"/>
            <Value active="True" name="autocorr_bern35-09"/>
            <Value active="True" name="autocorr_bern35-18"/>
            <Value active="True" name="autocorr_bern35-26"/>
            <Value active="True" name="autocorr_bern35-35"/>
            <Value active="True" name="autocorr_bern35-35fix"/>
            <Value active="True" name="autocorr_bern40-05"/>
            <Value active="True" name="autocorr_bern40-10"/>
            <Value active="True" name="autocorr_bern40-20"/>
            <Value active="True" name="autocorr_bern40-30"/>
            <Value active="True" name="autocorr_bern40-40"/>
            <Value active="True" name="autocorr_bern45-05"/>
            <Value active="True" name="autocorr_bern45-11"/>
            <Value active="True" name="autocorr_bern45-23"/>
            <Value active="True" name="autocorr_bern45-34"/>
            <Value active="True" name="autocorr_bern45-45"/>
            <Value active="True" name="autocorr_bern50-06"/>
            <Value active="True" name="autocorr_bern50-13"/>
            <Value active="True" name="autocorr_bern50-25"/>
            <Value active="True" name="autocorr_bern50-38"/>
            <Value active="True" name="autocorr_bern50-50"/>
            <Value active="True" name="autocorr_bern55-06"/>
            <Value active="True" name="autocorr_bern55-14"/>
            <Value active="True" name="autocorr_bern55-28"/>
            <Value active="True" name="autocorr_bern55-41"/>
            <Value active="True" name="autocorr_bern55-55"/>
            <Value active="True" name="autocorr_bern60-08"/>
            <Value active="True" name="autocorr_bern60-15"/>
            <Value active="True" name="autocorr_bern60-30"/>
            <Value active="True" name="autocorr_bern60-45"/>
            <Value active="True" name="autocorr_bern60-60"/>
            <Value active="True" name="batch0812_nc"/>
            <Value active="True" name="batch_nc"/>
            <Value active="True" name="bayes2_10"/>
            <Value active="True" name="bayes2_20"/>
            <Value active="True" name="bayes2_30"/>
            <Value active="True" name="bayes2_50"/>
            <Value active="True" name="bchoco05"/>
            <Value active="True" name="bchoco06"/>
            <Value active="True" name="bchoco07"/>
            <Value active="True" name="bchoco08"/>
            <Value active="True" name="bearing"/>
            <Value active="True" name="beuster"/>
            <Value active="True" name="blend029"/>
            <Value active="True" name="blend146"/>
            <Value active="True" name="blend480"/>
            <Value active="True" name="blend531"/>
            <Value active="True" name="blend718"/>
            <Value active="True" name="blend721"/>
            <Value active="True" name="blend852"/>
            <Value active="True" name="blendgap"/>
            <Value active="True" name="btest14"/>
            <Value active="True" name="camcns"/>
            <Value active="True" name="camshape100"/>
            <Value active="True" name="camshape200"/>
            <Value active="True" name="camshape400"/>
            <Value active="True" name="camshape800"/>
            <Value active="True" name="cardqp_inlp"/>
            <Value active="True" name="cardqp_iqp"/>
            <Value active="True" name="carton7"/>
            <Value active="True" name="carton9"/>
            <Value active="True" name="casctanks"/>
            <Value active="True" name="case_1scv2"/>
            <Value active="True" name="catmix100"/>
            <Value active="True" name="catmix200"/>
            <Value active="True" name="catmix400"/>
            <Value active="True" name="catmix800"/>
            <Value active="True" name="cecil_13"/>
            <Value active="True" name="celar6-sub0"/>
            <Value active="True" name="cesam2cent"/>
            <Value active="True" name="cesam2log"/>
            <Value active="True" name="chain100"/>
            <Value active="True" name="chain200"/>
            <Value active="True" name="chain400"/>
            <Value active="True" name="chain50"/>
            <Value active="True" name="chakra"/>
            <Value active="True" name="chenery"/>
            <Value active="True" name="chp_partload"/>
            <Value active="True" name="chp_shorttermplan1a"/>
            <Value active="True" name="chp_shorttermplan1b"/>
            <Value active="True" name="chp_shorttermplan2a"/>
            <Value active="True" name="chp_shorttermplan2b"/>
            <Value active="True" name="chp_shorttermplan2c"/>
            <Value active="True" name="chp_shorttermplan2d"/>
            <Value active="True" name="circle"/>
            <Value active="True" name="color_lab3_3x0"/>
            <Value active="True" name="color_lab3_4x0"/>
            <Value active="True" name="cont6-qq"/>
            <Value active="True" name="contvar"/>
            <Value active="True" name="crossdock_15x7"/>
            <Value active="True" name="crossdock_15x8"/>
            <Value active="True" name="crudeoil_lee1_05"/>
            <Value active="True" name="crudeoil_lee1_06"/>
            <Value active="True" name="crudeoil_lee1_07"/>
            <Value active="True" name="crudeoil_lee1_08"/>
            <Value active="True" name="crudeoil_lee1_09"/>
            <Value active="True" name="crudeoil_lee1_10"/>
            <Value active="True" name="crudeoil_lee2_05"/>
            <Value active="True" name="crudeoil_lee2_06"/>
            <Value active="True" name="crudeoil_lee2_07"/>
            <Value active="True" name="crudeoil_lee2_08"/>
            <Value active="True" name="crudeoil_lee2_09"/>
            <Value active="True" name="crudeoil_lee2_10"/>
            <Value active="True" name="crudeoil_lee3_05"/>
            <Value active="True" name="crudeoil_lee3_06"/>
            <Value active="True" name="crudeoil_lee3_07"/>
            <Value active="True" name="crudeoil_lee3_08"/>
            <Value active="True" name="crudeoil_lee3_09"/>
            <Value active="True" name="crudeoil_lee3_10"/>
            <Value active="True" name="crudeoil_lee4_05"/>
            <Value active="True" name="crudeoil_lee4_06"/>
            <Value active="True" name="crudeoil_lee4_07"/>
            <Value active="True" name="crudeoil_lee4_08"/>
            <Value active="True" name="crudeoil_lee4_09"/>
            <Value active="True" name="crudeoil_lee4_10"/>
            <Value active="True" name="crudeoil_li01"/>
            <Value active="True" name="crudeoil_li02"/>
            <Value active="True" name="crudeoil_li03"/>
            <Value active="True" name="crudeoil_li05"/>
            <Value active="True" name="crudeoil_li06"/>
            <Value active="True" name="crudeoil_li11"/>
            <Value active="True" name="crudeoil_li21"/>
            <Value active="True" name="crudeoil_pooling_ct1"/>
            <Value active="True" name="crudeoil_pooling_ct2"/>
            <Value active="True" name="crudeoil_pooling_ct3"/>
            <Value active="True" name="crudeoil_pooling_ct4"/>
            <Value active="True" name="crudeoil_pooling_dt1"/>
            <Value active="True" name="crudeoil_pooling_dt2"/>
            <Value active="True" name="crudeoil_pooling_dt3"/>
            <Value active="True" name="crudeoil_pooling_dt4"/>
            <Value active="True" name="csched1"/>
            <Value active="True" name="csched1a"/>
            <Value active="True" name="csched2"/>
            <Value active="True" name="csched2a"/>
            <Value active="True" name="deb10"/>
            <Value active="True" name="deb6"/>
            <Value active="True" name="deb7"/>
            <Value active="True" name="deb8"/>
            <Value active="True" name="deb9"/>
            <Value active="True" name="demo7"/>
            <Value active="True" name="dispatch"/>
            <Value active="True" name="dosemin2d"/>
            <Value active="True" name="dosemin3d"/>
            <Value active="True" name="dtoc5"/>
            <Value active="True" name="edgecross10-010"/>
            <Value active="True" name="edgecross10-020"/>
            <Value active="True" name="edgecross10-030"/>
            <Value active="True" name="edgecross10-040"/>
            <Value active="True" name="edgecross10-050"/>
            <Value active="True" name="edgecross10-060"/>
            <Value active="True" name="edgecross10-070"/>
            <Value active="True" name="edgecross10-080"/>
            <Value active="True" name="edgecross10-090"/>
            <Value active="True" name="edgecross14-019"/>
            <Value active="True" name="edgecross14-039"/>
            <Value active="True" name="edgecross14-058"/>
            <Value active="True" name="edgecross14-078"/>
            <Value active="True" name="edgecross14-098"/>
            <Value active="True" name="edgecross14-117"/>
            <Value active="True" name="edgecross14-137"/>
            <Value active="True" name="edgecross14-156"/>
            <Value active="True" name="edgecross14-176"/>
            <Value active="True" name="edgecross20-040"/>
            <Value active="True" name="edgecross20-080"/>
            <Value active="True" name="edgecross22-048"/>
            <Value active="True" name="edgecross22-096"/>
            <Value active="True" name="edgecross24-057"/>
            <Value active="True" name="edgecross24-115"/>
            <Value active="True" name="eg_all_s"/>
            <Value active="True" name="eg_disc2_s"/>
            <Value active="True" name="eg_disc_s"/>
            <Value active="True" name="eg_int_s"/>
            <Value active="True" name="eigena2"/>
            <Value active="True" name="elec100"/>
            <Value active="True" name="elec200"/>
            <Value active="True" name="elec25"/>
            <Value active="True" name="elec50"/>
            <Value active="True" name="elf"/>
            <Value active="True" name="emfl050_3_3"/>
            <Value active="True" name="emfl050_5_5"/>
            <Value active="True" name="emfl100_3_3"/>
            <Value active="True" name="emfl100_5_5"/>
            <Value active="True" name="eniplac"/>
            <Value active="True" name="eq6_1"/>
            <Value active="True" name="etamac"/>
            <Value active="True" name="ethanolh"/>
            <Value active="True" name="ethanolm"/>
            <Value active="True" name="ex1221"/>
            <Value active="True" name="ex1222"/>
            <Value active="True" name="ex1224"/>
            <Value active="True" name="ex1225"/>
            <Value active="True" name="ex1226"/>
            <Value active="True" name="ex1233"/>
            <Value active="True" name="ex1243"/>
            <Value active="True" name="ex1244"/>
            <Value active="True" name="ex1252"/>
            <Value active="True" name="ex1252a"/>
            <Value active="True" name="ex1263"/>
            <Value active="True" name="ex1263a"/>
            <Value active="True" name="ex1264"/>
            <Value active="True" name="ex1264a"/>
            <Value active="True" name="ex1265"/>
            <Value active="True" name="ex1265a"/>
            <Value active="True" name="ex1266"/>
            <Value active="True" name="ex1266a"/>
            <Value active="True" name="ex14_1_1"/>
            <Value active="True" name="ex14_1_2"/>
            <Value active="True" name="ex14_1_3"/>
            <Value active="True" name="ex14_1_4"/>
            <Value active="True" name="ex14_1_5"/>
            <Value active="True" name="ex14_1_6"/>
            <Value active="True" name="ex14_1_7"/>
            <Value active="True" name="ex14_1_8"/>
            <Value active="True" name="ex14_2_1"/>
            <Value active="True" name="ex14_2_2"/>
            <Value active="True" name="ex14_2_3"/>
            <Value active="True" name="ex14_2_4"/>
            <Value active="True" name="ex14_2_5"/>
            <Value active="True" name="ex14_2_6"/>
            <Value active="True" name="ex14_2_7"/>
            <Value active="True" name="ex14_2_8"/>
            <Value active="True" name="ex14_2_9"/>
            <Value active="True" name="ex2_1_1"/>
            <Value active="True" name="ex2_1_10"/>
            <Value active="True" name="ex2_1_2"/>
            <Value active="True" name="ex2_1_3"/>
            <Value active="True" name="ex2_1_4"/>
            <Value active="True" name="ex2_1_5"/>
            <Value active="True" name="ex2_1_6"/>
            <Value active="True" name="ex2_1_7"/>
            <Value active="True" name="ex2_1_8"/>
            <Value active="True" name="ex2_1_9"/>
            <Value active="True" name="ex3_1_1"/>
            <Value active="True" name="ex3_1_2"/>
            <Value active="True" name="ex3_1_3"/>
            <Value active="True" name="ex3_1_4"/>
            <Value active="True" name="ex3pb"/>
            <Value active="True" name="ex4_1_1"/>
            <Value active="True" name="ex4_1_2"/>
            <Value active="True" name="ex4_1_3"/>
            <Value active="True" name="ex4_1_7"/>
            <Value active="True" name="ex4_1_8"/>
            <Value active="True" name="ex4_1_9"/>
            <Value active="True" name="ex5_2_2_case1"/>
            <Value active="True" name="ex5_2_2_case2"/>
            <Value active="True" name="ex5_2_2_case3"/>
            <Value active="True" name="ex5_2_4"/>
            <Value active="True" name="ex5_2_5"/>
            <Value active="True" name="ex5_3_2"/>
            <Value active="True" name="ex5_3_3"/>
            <Value active="True" name="ex5_4_2"/>
            <Value active="True" name="ex5_4_3"/>
            <Value active="True" name="ex5_4_4"/>
            <Value active="True" name="ex6_1_1"/>
            <Value active="True" name="ex6_1_2"/>
            <Value active="True" name="ex6_1_3"/>
            <Value active="True" name="ex6_1_4"/>
            <Value active="True" name="ex6_2_10"/>
            <Value active="True" name="ex6_2_11"/>
            <Value active="True" name="ex6_2_12"/>
            <Value active="True" name="ex6_2_14"/>
            <Value active="True" name="ex6_2_5"/>
            <Value active="True" name="ex6_2_6"/>
            <Value active="True" name="ex6_2_7"/>
            <Value active="True" name="ex6_2_8"/>
            <Value active="True" name="ex6_2_9"/>
            <Value active="True" name="ex7_2_1"/>
            <Value active="True" name="ex7_2_2"/>
            <Value active="True" name="ex7_2_3"/>
            <Value active="True" name="ex7_2_4"/>
            <Value active="True" name="ex7_3_1"/>
            <Value active="True" name="ex7_3_2"/>
            <Value active="True" name="ex7_3_3"/>
            <Value active="True" name="ex7_3_4"/>
            <Value active="True" name="ex7_3_5"/>
            <Value active="True" name="ex7_3_6"/>
            <Value active="True" name="ex8_1_1"/>
            <Value active="True" name="ex8_1_2"/>
            <Value active="True" name="ex8_1_5"/>
            <Value active="True" name="ex8_1_6"/>
            <Value active="True" name="ex8_1_7"/>
            <Value active="True" name="ex8_2_1b"/>
            <Value active="True" name="ex8_2_2b"/>
            <Value active="True" name="ex8_2_3b"/>
            <Value active="True" name="ex8_2_4b"/>
            <Value active="True" name="ex8_2_5b"/>
            <Value active="True" name="ex8_3_1"/>
            <Value active="True" name="ex8_3_11"/>
            <Value active="True" name="ex8_3_12"/>
            <Value active="True" name="ex8_3_13"/>
            <Value active="True" name="ex8_3_14"/>
            <Value active="True" name="ex8_3_2"/>
            <Value active="True" name="ex8_3_3"/>
            <Value active="True" name="ex8_3_4"/>
            <Value active="True" name="ex8_3_5"/>
            <Value active="True" name="ex8_3_7"/>
            <Value active="True" name="ex8_3_8"/>
            <Value active="True" name="ex8_3_9"/>
            <Value active="True" name="ex8_4_1"/>
            <Value active="True" name="ex8_4_2"/>
            <Value active="True" name="ex8_4_3"/>
            <Value active="True" name="ex8_4_4"/>
            <Value active="True" name="ex8_4_5"/>
            <Value active="True" name="ex8_4_6"/>
            <Value active="True" name="ex8_4_7"/>
            <Value active="True" name="ex8_4_8_bnd"/>
            <Value active="True" name="ex8_5_1"/>
            <Value active="True" name="ex8_5_2"/>
            <Value active="True" name="ex8_5_3"/>
            <Value active="True" name="ex8_5_4"/>
            <Value active="True" name="ex8_5_5"/>
            <Value active="True" name="ex8_5_6"/>
            <Value active="True" name="ex8_6_1"/>
            <Value active="True" name="ex8_6_2"/>
            <Value active="True" name="ex9_1_1"/>
            <Value active="True" name="ex9_1_2"/>
            <Value active="True" name="ex9_1_4"/>
            <Value active="True" name="ex9_1_5"/>
            <Value active="True" name="ex9_1_8"/>
            <Value active="True" name="ex9_2_2"/>
            <Value active="True" name="ex9_2_3"/>
            <Value active="True" name="ex9_2_4"/>
            <Value active="True" name="ex9_2_5"/>
            <Value active="True" name="ex9_2_6"/>
            <Value active="True" name="ex9_2_7"/>
            <Value active="True" name="ex9_2_8"/>
            <Value active="True" name="faclay20h"/>
            <Value active="True" name="faclay25"/>
            <Value active="True" name="faclay30"/>
            <Value active="True" name="faclay30h"/>
            <Value active="True" name="faclay33"/>
            <Value active="True" name="faclay35"/>
            <Value active="True" name="faclay60"/>
            <Value active="True" name="faclay70"/>
            <Value active="True" name="faclay75"/>
            <Value active="True" name="faclay80"/>
            <Value active="True" name="fct"/>
            <Value active="True" name="fdesign10"/>
            <Value active="True" name="fdesign25"/>
            <Value active="True" name="fdesign50"/>
            <Value active="True" name="feedtray"/>
            <Value active="True" name="feedtray2"/>
            <Value active="True" name="filter"/>
            <Value active="True" name="fin2bb"/>
            <Value active="True" name="flowchan100fix"/>
            <Value active="True" name="flowchan200fix"/>
            <Value active="True" name="flowchan400fix"/>
            <Value active="True" name="flowchan50fix"/>
            <Value active="True" name="forest"/>
            <Value active="True" name="fuel"/>
            <Value active="True" name="fuzzy"/>
            <Value active="True" name="gabriel01"/>
            <Value active="True" name="gabriel02"/>
            <Value active="True" name="gabriel04"/>
            <Value active="True" name="gabriel05"/>
            <Value active="True" name="gabriel06"/>
            <Value active="True" name="gabriel07"/>
            <Value active="True" name="gabriel08"/>
            <Value active="True" name="gabriel09"/>
            <Value active="True" name="gabriel10"/>
            <Value active="True" name="gams02"/>
            <Value active="True" name="gams03"/>
            <Value active="True" name="gancns"/>
            <Value active="True" name="gasnet"/>
            <Value active="True" name="gasnet_al1"/>
            <Value active="True" name="gasnet_al2"/>
            <Value active="True" name="gasnet_al3"/>
            <Value active="True" name="gasnet_al4"/>
            <Value active="True" name="gasnet_al5"/>
            <Value active="True" name="gasoil100"/>
            <Value active="True" name="gasoil200"/>
            <Value active="True" name="gasoil400"/>
            <Value active="True" name="gasoil50"/>
            <Value active="True" name="gasprod_sarawak01"/>
            <Value active="True" name="gasprod_sarawak16"/>
            <Value active="True" name="gasprod_sarawak81"/>
            <Value active="True" name="gastrans"/>
            <Value active="True" name="gastrans040"/>
            <Value active="True" name="gastrans135"/>
            <Value active="True" name="gastrans582_cold13"/>
            <Value active="True" name="gastrans582_cold13_95"/>
            <Value active="True" name="gastrans582_cold17"/>
            <Value active="True" name="gastrans582_cold17_95"/>
            <Value active="True" name="gastrans582_cool12"/>
            <Value active="True" name="gastrans582_cool12_95"/>
            <Value active="True" name="gastrans582_cool14"/>
            <Value active="True" name="gastrans582_cool14_95"/>
            <Value active="True" name="gastrans582_freezing27"/>
            <Value active="True" name="gastrans582_freezing27_95"/>
            <Value active="True" name="gastrans582_freezing30"/>
            <Value active="True" name="gastrans582_freezing30_95"/>
            <Value active="True" name="gastrans582_mild10"/>
            <Value active="True" name="gastrans582_mild10_95"/>
            <Value active="True" name="gastrans582_mild11"/>
            <Value active="True" name="gastrans582_mild11_95"/>
            <Value active="True" name="gastrans582_warm15"/>
            <Value active="True" name="gastrans582_warm15_95"/>
            <Value active="True" name="gastrans582_warm31"/>
            <Value active="True" name="gastrans582_warm31_95"/>
            <Value active="True" name="gastransnlp"/>
            <Value active="True" name="gear4"/>
            <Value active="True" name="genpooling_lee1"/>
            <Value active="True" name="genpooling_lee2"/>
            <Value active="True" name="genpooling_meyer04"/>
            <Value active="True" name="genpooling_meyer10"/>
            <Value active="True" name="genpooling_meyer15"/>
            <Value active="True" name="ghg_1veh"/>
            <Value active="True" name="ghg_2veh"/>
            <Value active="True" name="ghg_3veh"/>
            <Value active="True" name="gilbert"/>
            <Value active="True" name="gkocis"/>
            <Value active="True" name="glider100"/>
            <Value active="True" name="glider200"/>
            <Value active="True" name="glider400"/>
            <Value active="True" name="glider50"/>
            <Value active="True" name="graphpart_2g-0044-1601"/>
            <Value active="True" name="graphpart_2g-0055-0062"/>
            <Value active="True" name="graphpart_2g-0066-0066"/>
            <Value active="True" name="graphpart_2g-0077-0077"/>
            <Value active="True" name="graphpart_2g-0088-0088"/>
            <Value active="True" name="graphpart_2g-0099-9211"/>
            <Value active="True" name="graphpart_2g-1010-0824"/>
            <Value active="True" name="graphpart_2pm-0044-0044"/>
            <Value active="True" name="graphpart_2pm-0055-0055"/>
            <Value active="True" name="graphpart_2pm-0066-0066"/>
            <Value active="True" name="graphpart_2pm-0077-0777"/>
            <Value active="True" name="graphpart_2pm-0088-0888"/>
            <Value active="True" name="graphpart_2pm-0099-0999"/>
            <Value active="True" name="graphpart_3g-0234-0234"/>
            <Value active="True" name="graphpart_3g-0244-0244"/>
            <Value active="True" name="graphpart_3g-0333-0333"/>
            <Value active="True" name="graphpart_3g-0334-0334"/>
            <Value active="True" name="graphpart_3g-0344-0344"/>
            <Value active="True" name="graphpart_3g-0444-0444"/>
            <Value active="True" name="graphpart_3pm-0234-0234"/>
            <Value active="True" name="graphpart_3pm-0244-0244"/>
            <Value active="True" name="graphpart_3pm-0333-0333"/>
            <Value active="True" name="graphpart_3pm-0334-0334"/>
            <Value active="True" name="graphpart_3pm-0344-0344"/>
            <Value active="True" name="graphpart_3pm-0444-0444"/>
            <Value active="True" name="graphpart_clique-20"/>
            <Value active="True" name="graphpart_clique-30"/>
            <Value active="True" name="graphpart_clique-40"/>
            <Value active="True" name="graphpart_clique-50"/>
            <Value active="True" name="graphpart_clique-60"/>
            <Value active="True" name="graphpart_clique-70"/>
            <Value active="True" name="gsg_0001"/>
            <Value active="True" name="hadamard_4"/>
            <Value active="True" name="hadamard_5"/>
            <Value active="True" name="hadamard_6"/>
            <Value active="True" name="hadamard_8"/>
            <Value active="True" name="hadamard_9"/>
            <Value active="True" name="haverly"/>
            <Value active="True" name="hda"/>
            <Value active="True" name="heatexch_gen1"/>
            <Value active="True" name="heatexch_gen2"/>
            <Value active="True" name="heatexch_gen3"/>
            <Value active="True" name="heatexch_spec1"/>
            <Value active="True" name="heatexch_spec2"/>
            <Value active="True" name="heatexch_spec3"/>
            <Value active="True" name="heatexch_trigen"/>
            <Value active="True" name="hhfair"/>
            <Value active="True" name="himmel11"/>
            <Value active="True" name="himmel16"/>
            <Value active="True" name="hmittelman"/>
            <Value active="True" name="house"/>
            <Value active="True" name="hs62"/>
            <Value active="True" name="hvb11"/>
            <Value active="True" name="hvycrash"/>
            <Value active="True" name="hybriddynamic_fixedcc"/>
            <Value active="True" name="hybriddynamic_var"/>
            <Value active="True" name="hybriddynamic_varcc"/>
            <Value active="True" name="hydro"/>
            <Value active="True" name="hydroenergy1"/>
            <Value active="True" name="hydroenergy2"/>
            <Value active="True" name="hydroenergy3"/>
            <Value active="True" name="infeas1"/>
            <Value active="True" name="ising2_5-300_5555"/>
            <Value active="True" name="johnall"/>
            <Value active="True" name="junkturn"/>
            <Value active="True" name="kall_circles_c6a"/>
            <Value active="True" name="kall_circles_c6b"/>
            <Value active="True" name="kall_circles_c6c"/>
            <Value active="True" name="kall_circles_c7a"/>
            <Value active="True" name="kall_circles_c8a"/>
            <Value active="True" name="kall_circlespolygons_c1p11"/>
            <Value active="True" name="kall_circlespolygons_c1p12"/>
            <Value active="True" name="kall_circlespolygons_c1p13"/>
            <Value active="True" name="kall_circlespolygons_c1p5a"/>
            <Value active="True" name="kall_circlespolygons_c1p5b"/>
            <Value active="True" name="kall_circlespolygons_c1p6a"/>
            <Value active="True" name="kall_circlesrectangles_c1r11"/>
            <Value active="True" name="kall_circlesrectangles_c1r12"/>
            <Value active="True" name="kall_circlesrectangles_c1r13"/>
            <Value active="True" name="kall_circlesrectangles_c6r1"/>
            <Value active="True" name="kall_circlesrectangles_c6r29"/>
            <Value active="True" name="kall_circlesrectangles_c6r39"/>
            <Value active="True" name="kall_congruentcircles_c31"/>
            <Value active="True" name="kall_congruentcircles_c32"/>
            <Value active="True" name="kall_congruentcircles_c41"/>
            <Value active="True" name="kall_congruentcircles_c42"/>
            <Value active="True" name="kall_congruentcircles_c51"/>
            <Value active="True" name="kall_congruentcircles_c52"/>
            <Value active="True" name="kall_congruentcircles_c61"/>
            <Value active="True" name="kall_congruentcircles_c62"/>
            <Value active="True" name="kall_congruentcircles_c63"/>
            <Value active="True" name="kall_congruentcircles_c71"/>
            <Value active="True" name="kall_congruentcircles_c72"/>
            <Value active="True" name="kall_diffcircles_10"/>
            <Value active="True" name="kall_diffcircles_5a"/>
            <Value active="True" name="kall_diffcircles_5b"/>
            <Value active="True" name="kall_diffcircles_6"/>
            <Value active="True" name="kall_diffcircles_7"/>
            <Value active="True" name="kall_diffcircles_8"/>
            <Value active="True" name="kall_diffcircles_9"/>
            <Value active="True" name="kall_ellipsoids_tc02b"/>
            <Value active="True" name="kall_ellipsoids_tc03c"/>
            <Value active="True" name="kall_ellipsoids_tc05a"/>
            <Value active="True" name="kissing2"/>
            <Value active="True" name="knp3-12"/>
            <Value active="True" name="knp4-24"/>
            <Value active="True" name="knp5-40"/>
            <Value active="True" name="knp5-41"/>
            <Value active="True" name="knp5-42"/>
            <Value active="True" name="knp5-43"/>
            <Value active="True" name="knp5-44"/>
            <Value active="True" name="korcns"/>
            <Value active="True" name="kport20"/>
            <Value active="True" name="kport40"/>
            <Value active="True" name="lakes"/>
            <Value active="True" name="launch"/>
            <Value active="True" name="least"/>
            <Value active="True" name="lip"/>
            <Value active="True" name="lnts100"/>
            <Value active="True" name="lnts200"/>
            <Value active="True" name="lnts400"/>
            <Value active="True" name="lnts50"/>
            <Value active="True" name="lop97ic"/>
            <Value active="True" name="lop97icx"/>
            <Value active="True" name="lukvle10"/>
            <Value active="True" name="mathopt1"/>
            <Value active="True" name="mathopt2"/>
            <Value active="True" name="mathopt3"/>
            <Value active="True" name="mathopt4"/>
            <Value active="True" name="mathopt5_3"/>
            <Value active="True" name="mathopt5_7"/>
            <Value active="True" name="maxcsp-ehi-85-297-12"/>
            <Value active="True" name="maxcsp-ehi-85-297-36"/>
            <Value active="True" name="maxcsp-ehi-85-297-71"/>
            <Value active="True" name="maxcsp-ehi-90-315-70"/>
            <Value active="True" name="maxcsp-geo50-20-d4-75-36"/>
            <Value active="True" name="maxcsp-langford-3-11"/>
            <Value active="True" name="maxmin"/>
            <Value active="True" name="maxmineig2"/>
            <Value active="True" name="mbtd"/>
            <Value active="True" name="meanvar-orl400_05_e_7"/>
            <Value active="True" name="methanol100"/>
            <Value active="True" name="methanol200"/>
            <Value active="True" name="methanol400"/>
            <Value active="True" name="methanol50"/>
            <Value active="True" name="mhw4d"/>
            <Value active="True" name="milinfract"/>
            <Value active="True" name="minlphi"/>
            <Value active="True" name="minlphix"/>
            <Value active="True" name="multiplants_mtg1a"/>
            <Value active="True" name="multiplants_mtg1b"/>
            <Value active="True" name="multiplants_mtg1c"/>
            <Value active="True" name="multiplants_mtg2"/>
            <Value active="True" name="multiplants_mtg5"/>
            <Value active="True" name="multiplants_mtg6"/>
            <Value active="True" name="multiplants_stg1"/>
            <Value active="True" name="multiplants_stg1a"/>
            <Value active="True" name="multiplants_stg1b"/>
            <Value active="True" name="multiplants_stg1c"/>
            <Value active="True" name="multiplants_stg5"/>
            <Value active="True" name="multiplants_stg6"/>
            <Value active="True" name="nd_netgen-2000-2-5-a-a-ns_7"/>
            <Value active="True" name="nd_netgen-2000-3-4-b-a-ns_7"/>
            <Value active="True" name="nd_netgen-3000-1-1-b-b-ns_7"/>
            <Value active="True" name="ndcc12"/>
            <Value active="True" name="ndcc12persp"/>
            <Value active="True" name="ndcc13"/>
            <Value active="True" name="ndcc13persp"/>
            <Value active="True" name="ndcc14"/>
            <Value active="True" name="ndcc14persp"/>
            <Value active="True" name="ndcc15"/>
            <Value active="True" name="ndcc15persp"/>
            <Value active="True" name="ndcc16"/>
            <Value active="True" name="ndcc16persp"/>
            <Value active="True" name="nemhaus"/>
            <Value active="True" name="ngone"/>
            <Value active="True" name="nous1"/>
            <Value active="True" name="nous2"/>
            <Value active="True" name="nuclear104"/>
            <Value active="True" name="nuclear10a"/>
            <Value active="True" name="nuclear10b"/>
            <Value active="True" name="nuclear14"/>
            <Value active="True" name="nuclear14a"/>
            <Value active="True" name="nuclear14b"/>
            <Value active="True" name="nuclear25"/>
            <Value active="True" name="nuclear25a"/>
            <Value active="True" name="nuclear25b"/>
            <Value active="True" name="nuclear49"/>
            <Value active="True" name="nuclear49a"/>
            <Value active="True" name="nuclear49b"/>
            <Value active="True" name="nuclearva"/>
            <Value active="True" name="nuclearvb"/>
            <Value active="True" name="nuclearvc"/>
            <Value active="True" name="nuclearvd"/>
            <Value active="True" name="nuclearve"/>
            <Value active="True" name="nuclearvf"/>
            <Value active="True" name="nvs01"/>
            <Value active="True" name="nvs02"/>
            <Value active="True" name="nvs05"/>
            <Value active="True" name="nvs07"/>
            <Value active="True" name="nvs08"/>
            <Value active="True" name="nvs13"/>
            <Value active="True" name="nvs14"/>
            <Value active="True" name="nvs16"/>
            <Value active="True" name="nvs17"/>
            <Value active="True" name="nvs18"/>
            <Value active="True" name="nvs19"/>
            <Value active="True" name="nvs21"/>
            <Value active="True" name="nvs22"/>
            <Value active="True" name="nvs23"/>
            <Value active="True" name="nvs24"/>
            <Value active="True" name="oaer"/>
            <Value active="True" name="oil"/>
            <Value active="True" name="oil2"/>
            <Value active="True" name="optcdeg2"/>
            <Value active="True" name="optmass"/>
            <Value active="True" name="ortez"/>
            <Value active="True" name="orth_d3m6"/>
            <Value active="True" name="orth_d3m6_pl"/>
            <Value active="True" name="orth_d4m6_pl"/>
            <Value active="True" name="otpop"/>
            <Value active="True" name="parabol5_2_2"/>
            <Value active="True" name="parabol5_2_3"/>
            <Value active="True" name="parabol5_2_4"/>
            <Value active="True" name="parabol_p"/>
            <Value active="True" name="parallel"/>
            <Value active="True" name="pb302035"/>
            <Value active="True" name="pb302055"/>
            <Value active="True" name="pb302075"/>
            <Value active="True" name="pb302095"/>
            <Value active="True" name="pb351535"/>
            <Value active="True" name="pb351555"/>
            <Value active="True" name="pb351575"/>
            <Value active="True" name="pb351595"/>
            <Value active="True" name="pindyck"/>
            <Value active="True" name="pinene100"/>
            <Value active="True" name="pinene200"/>
            <Value active="True" name="pinene50"/>
            <Value active="True" name="pointpack02"/>
            <Value active="True" name="pointpack04"/>
            <Value active="True" name="pointpack06"/>
            <Value active="True" name="pointpack08"/>
            <Value active="True" name="pointpack10"/>
            <Value active="True" name="pointpack12"/>
            <Value active="True" name="pointpack14"/>
            <Value active="True" name="polygon100"/>
            <Value active="True" name="polygon25"/>
            <Value active="True" name="polygon50"/>
            <Value active="True" name="polygon75"/>
            <Value active="True" name="pooling_adhya1pq"/>
            <Value active="True" name="pooling_adhya1stp"/>
            <Value active="True" name="pooling_adhya1tp"/>
            <Value active="True" name="pooling_adhya2pq"/>
            <Value active="True" name="pooling_adhya2stp"/>
            <Value active="True" name="pooling_adhya2tp"/>
            <Value active="True" name="pooling_adhya3pq"/>
            <Value active="True" name="pooling_adhya3stp"/>
            <Value active="True" name="pooling_adhya3tp"/>
            <Value active="True" name="pooling_adhya4pq"/>
            <Value active="True" name="pooling_adhya4stp"/>
            <Value active="True" name="pooling_adhya4tp"/>
            <Value active="True" name="pooling_bental4pq"/>
            <Value active="True" name="pooling_bental4stp"/>
            <Value active="True" name="pooling_bental4tp"/>
            <Value active="True" name="pooling_bental5pq"/>
            <Value active="True" name="pooling_bental5stp"/>
            <Value active="True" name="pooling_bental5tp"/>
            <Value active="True" name="pooling_digabel16"/>
            <Value active="True" name="pooling_digabel18"/>
            <Value active="True" name="pooling_digabel19"/>
            <Value active="True" name="pooling_epa1"/>
            <Value active="True" name="pooling_epa2"/>
            <Value active="True" name="pooling_epa3"/>
            <Value active="True" name="pooling_foulds2pq"/>
            <Value active="True" name="pooling_foulds2stp"/>
            <Value active="True" name="pooling_foulds2tp"/>
            <Value active="True" name="pooling_foulds3pq"/>
            <Value active="True" name="pooling_foulds3stp"/>
            <Value active="True" name="pooling_foulds3tp"/>
            <Value active="True" name="pooling_foulds4pq"/>
            <Value active="True" name="pooling_foulds4stp"/>
            <Value active="True" name="pooling_foulds4tp"/>
            <Value active="True" name="pooling_foulds5pq"/>
            <Value active="True" name="pooling_foulds5stp"/>
            <Value active="True" name="pooling_foulds5tp"/>
            <Value active="True" name="pooling_haverly1pq"/>
            <Value active="True" name="pooling_haverly1stp"/>
            <Value active="True" name="pooling_haverly1tp"/>
            <Value active="True" name="pooling_haverly2pq"/>
            <Value active="True" name="pooling_haverly2stp"/>
            <Value active="True" name="pooling_haverly2tp"/>
            <Value active="True" name="pooling_haverly3pq"/>
            <Value active="True" name="pooling_haverly3stp"/>
            <Value active="True" name="pooling_haverly3tp"/>
            <Value active="True" name="pooling_rt2pq"/>
            <Value active="True" name="pooling_rt2stp"/>
            <Value active="True" name="pooling_rt2tp"/>
            <Value active="True" name="pooling_sppa0pq"/>
            <Value active="True" name="pooling_sppa0stp"/>
            <Value active="True" name="pooling_sppa0tp"/>
            <Value active="True" name="pooling_sppa5pq"/>
            <Value active="True" name="pooling_sppa5stp"/>
            <Value active="True" name="pooling_sppa5tp"/>
            <Value active="True" name="pooling_sppa9pq"/>
            <Value active="True" name="pooling_sppa9stp"/>
            <Value active="True" name="pooling_sppa9tp"/>
            <Value active="True" name="pooling_sppb0pq"/>
            <Value active="True" name="pooling_sppb0stp"/>
            <Value active="True" name="pooling_sppb0tp"/>
            <Value active="True" name="pooling_sppb2pq"/>
            <Value active="True" name="pooling_sppb2stp"/>
            <Value active="True" name="pooling_sppb2tp"/>
            <Value active="True" name="pooling_sppb5pq"/>
            <Value active="True" name="pooling_sppb5stp"/>
            <Value active="True" name="pooling_sppb5tp"/>
            <Value active="True" name="pooling_sppc0pq"/>
            <Value active="True" name="pooling_sppc0stp"/>
            <Value active="True" name="pooling_sppc0tp"/>
            <Value active="True" name="pooling_sppc1pq"/>
            <Value active="True" name="pooling_sppc1stp"/>
            <Value active="True" name="pooling_sppc1tp"/>
            <Value active="True" name="pooling_sppc3pq"/>
            <Value active="True" name="pooling_sppc3stp"/>
            <Value active="True" name="pooling_sppc3tp"/>
            <Value active="True" name="popdynm100"/>
            <Value active="True" name="popdynm200"/>
            <Value active="True" name="popdynm25"/>
            <Value active="True" name="popdynm50"/>
            <Value active="True" name="portfol_robust050_34"/>
            <Value active="True" name="portfol_robust100_09"/>
            <Value active="True" name="portfol_robust200_03"/>
            <Value active="True" name="portfol_shortfall050_68"/>
            <Value active="True" name="portfol_shortfall100_04"/>
            <Value active="True" name="portfol_shortfall200_05"/>
            <Value active="True" name="powerflow0009p"/>
            <Value active="True" name="powerflow0009r"/>
            <Value active="True" name="powerflow0014p"/>
            <Value active="True" name="powerflow0014r"/>
            <Value active="True" name="powerflow0030p"/>
            <Value active="True" name="powerflow0030r"/>
            <Value active="True" name="powerflow0039p"/>
            <Value active="True" name="powerflow0039r"/>
            <Value active="True" name="powerflow0057p"/>
            <Value active="True" name="powerflow0057r"/>
            <Value active="True" name="powerflow0118p"/>
            <Value active="True" name="powerflow0118r"/>
            <Value active="True" name="powerflow0300p"/>
            <Value active="True" name="powerflow0300r"/>
            <Value active="True" name="powerflow2383wpp"/>
            <Value active="True" name="powerflow2383wpr"/>
            <Value active="True" name="powerflow2736spp"/>
            <Value active="True" name="powerflow2736spr"/>
            <Value active="True" name="primary"/>
            <Value active="True" name="prob02"/>
            <Value active="True" name="prob03"/>
            <Value active="True" name="prob06"/>
            <Value active="True" name="prob07"/>
            <Value active="True" name="prob09"/>
            <Value active="True" name="process"/>
            <Value active="True" name="procsel"/>
            <Value active="True" name="product"/>
            <Value active="True" name="product2"/>
            <Value active="True" name="prolog"/>
            <Value active="True" name="qap"/>
            <Value active="True" name="qapw"/>
            <Value active="True" name="qp3"/>
            <Value active="True" name="qspp_0_10_0_1_10_1"/>
            <Value active="True" name="qspp_0_11_0_1_10_1"/>
            <Value active="True" name="qspp_0_12_0_1_10_1"/>
            <Value active="True" name="qspp_0_13_0_1_10_1"/>
            <Value active="True" name="qspp_0_14_0_1_10_1"/>
            <Value active="True" name="qspp_0_15_0_1_10_1"/>
            <Value active="True" name="radar-2000-10-a-6_lat_7"/>
            <Value active="True" name="radar-3000-10-a-8_lat_7"/>
            <Value active="True" name="ramsey"/>
            <Value active="True" name="ringpack_10_1"/>
            <Value active="True" name="ringpack_10_2"/>
            <Value active="True" name="ringpack_20_1"/>
            <Value active="True" name="ringpack_20_2"/>
            <Value active="True" name="ringpack_20_3"/>
            <Value active="True" name="ringpack_30_1"/>
            <Value active="True" name="ringpack_30_2"/>
            <Value active="True" name="robot100"/>
            <Value active="True" name="robot200"/>
            <Value active="True" name="robot400"/>
            <Value active="True" name="robot50"/>
            <Value active="True" name="rocket100"/>
            <Value active="True" name="rocket200"/>
            <Value active="True" name="rocket400"/>
            <Value active="True" name="rocket50"/>
            <Value active="True" name="routingdelay_proj"/>
            <Value active="True" name="saa_2"/>
            <Value active="True" name="sep1"/>
            <Value active="True" name="sepasequ_complex"/>
            <Value active="True" name="sepasequ_convent"/>
            <Value active="True" name="sfacloc1_2_80"/>
            <Value active="True" name="sfacloc1_2_90"/>
            <Value active="True" name="sfacloc1_2_95"/>
            <Value active="True" name="sfacloc1_3_80"/>
            <Value active="True" name="sfacloc1_3_90"/>
            <Value active="True" name="sfacloc1_3_95"/>
            <Value active="True" name="sfacloc1_4_80"/>
            <Value active="True" name="sfacloc1_4_90"/>
            <Value active="True" name="sfacloc1_4_95"/>
            <Value active="True" name="sfacloc2_2_80"/>
            <Value active="True" name="sfacloc2_2_90"/>
            <Value active="True" name="sfacloc2_2_95"/>
            <Value active="True" name="sfacloc2_3_80"/>
            <Value active="True" name="sfacloc2_3_90"/>
            <Value active="True" name="sfacloc2_3_95"/>
            <Value active="True" name="sfacloc2_4_80"/>
            <Value active="True" name="sfacloc2_4_90"/>
            <Value active="True" name="sfacloc2_4_95"/>
            <Value active="True" name="shiporig"/>
            <Value active="True" name="sjup2"/>
            <Value active="True" name="smallinvSNPr1b010-011"/>
            <Value active="True" name="smallinvSNPr1b020-022"/>
            <Value active="True" name="smallinvSNPr1b050-055"/>
            <Value active="True" name="smallinvSNPr1b100-110"/>
            <Value active="True" name="smallinvSNPr1b150-165"/>
            <Value active="True" name="smallinvSNPr1b200-220"/>
            <Value active="True" name="smallinvSNPr2b010-011"/>
            <Value active="True" name="smallinvSNPr2b020-022"/>
            <Value active="True" name="smallinvSNPr2b050-055"/>
            <Value active="True" name="smallinvSNPr2b100-110"/>
            <Value active="True" name="smallinvSNPr2b150-165"/>
            <Value active="True" name="smallinvSNPr2b200-220"/>
            <Value active="True" name="smallinvSNPr3b010-011"/>
            <Value active="True" name="smallinvSNPr3b020-022"/>
            <Value active="True" name="smallinvSNPr3b050-055"/>
            <Value active="True" name="smallinvSNPr3b100-110"/>
            <Value active="True" name="smallinvSNPr3b150-165"/>
            <Value active="True" name="smallinvSNPr3b200-220"/>
            <Value active="True" name="smallinvSNPr4b010-011"/>
            <Value active="True" name="smallinvSNPr4b020-022"/>
            <Value active="True" name="smallinvSNPr4b050-055"/>
            <Value active="True" name="smallinvSNPr4b100-110"/>
            <Value active="True" name="smallinvSNPr4b150-165"/>
            <Value active="True" name="smallinvSNPr4b200-220"/>
            <Value active="True" name="smallinvSNPr5b010-011"/>
            <Value active="True" name="smallinvSNPr5b020-022"/>
            <Value active="True" name="smallinvSNPr5b050-055"/>
            <Value active="True" name="smallinvSNPr5b100-110"/>
            <Value active="True" name="smallinvSNPr5b150-165"/>
            <Value active="True" name="smallinvSNPr5b200-220"/>
            <Value active="True" name="sonet17v4"/>
            <Value active="True" name="sonet18v6"/>
            <Value active="True" name="sonet19v5"/>
            <Value active="True" name="sonet20v6"/>
            <Value active="True" name="sonet21v6"/>
            <Value active="True" name="sonet22v4"/>
            <Value active="True" name="sonet22v5"/>
            <Value active="True" name="sonet23v4"/>
            <Value active="True" name="sonet23v6"/>
            <Value active="True" name="sonet24v2"/>
            <Value active="True" name="sonet24v5"/>
            <Value active="True" name="sonet25v5"/>
            <Value active="True" name="sonet25v6"/>
            <Value active="True" name="sonetgr17"/>
            <Value active="True" name="space25"/>
            <Value active="True" name="space25a"/>
            <Value active="True" name="space960"/>
            <Value active="True" name="spectra2"/>
            <Value active="True" name="sporttournament06"/>
            <Value active="True" name="sporttournament08"/>
            <Value active="True" name="sporttournament10"/>
            <Value active="True" name="sporttournament12"/>
            <Value active="True" name="sporttournament14"/>
            <Value active="True" name="sporttournament16"/>
            <Value active="True" name="sporttournament18"/>
            <Value active="True" name="sporttournament20"/>
            <Value active="True" name="sporttournament22"/>
            <Value active="True" name="sporttournament24"/>
            <Value active="True" name="sporttournament26"/>
            <Value active="True" name="sporttournament28"/>
            <Value active="True" name="sporttournament30"/>
            <Value active="True" name="sporttournament32"/>
            <Value active="True" name="sporttournament34"/>
            <Value active="True" name="sporttournament36"/>
            <Value active="True" name="sporttournament38"/>
            <Value active="True" name="sporttournament40"/>
            <Value active="True" name="sporttournament42"/>
            <Value active="True" name="sporttournament44"/>
            <Value active="True" name="sporttournament46"/>
            <Value active="True" name="sporttournament48"/>
            <Value active="True" name="sporttournament50"/>
            <Value active="True" name="spring"/>
            <Value active="True" name="squfl010-025persp"/>
            <Value active="True" name="squfl010-040persp"/>
            <Value active="True" name="squfl010-080persp"/>
            <Value active="True" name="squfl015-060persp"/>
            <Value active="True" name="squfl015-080persp"/>
            <Value active="True" name="squfl020-040persp"/>
            <Value active="True" name="squfl020-050persp"/>
            <Value active="True" name="squfl020-150persp"/>
            <Value active="True" name="squfl025-025persp"/>
            <Value active="True" name="squfl025-030persp"/>
            <Value active="True" name="squfl025-040persp"/>
            <Value active="True" name="squfl030-100persp"/>
            <Value active="True" name="squfl030-150persp"/>
            <Value active="True" name="squfl040-080persp"/>
            <Value active="True" name="sssd08-04persp"/>
            <Value active="True" name="sssd12-05persp"/>
            <Value active="True" name="sssd15-04persp"/>
            <Value active="True" name="sssd15-06persp"/>
            <Value active="True" name="sssd15-08persp"/>
            <Value active="True" name="sssd16-07persp"/>
            <Value active="True" name="sssd18-06persp"/>
            <Value active="True" name="sssd18-08persp"/>
            <Value active="True" name="sssd20-04persp"/>
            <Value active="True" name="sssd20-08persp"/>
            <Value active="True" name="sssd22-08persp"/>
            <Value active="True" name="sssd25-04persp"/>
            <Value active="True" name="sssd25-08persp"/>
            <Value active="True" name="st_bpaf1a"/>
            <Value active="True" name="st_bpaf1b"/>
            <Value active="True" name="st_bpk1"/>
            <Value active="True" name="st_bpv1"/>
            <Value active="True" name="st_bpv2"/>
            <Value active="True" name="st_bsj2"/>
            <Value active="True" name="st_bsj3"/>
            <Value active="True" name="st_bsj4"/>
            <Value active="True" name="st_e01"/>
            <Value active="True" name="st_e02"/>
            <Value active="True" name="st_e03"/>
            <Value active="True" name="st_e04"/>
            <Value active="True" name="st_e05"/>
            <Value active="True" name="st_e06"/>
            <Value active="True" name="st_e07"/>
            <Value active="True" name="st_e08"/>
            <Value active="True" name="st_e09"/>
            <Value active="True" name="st_e11"/>
            <Value active="True" name="st_e12"/>
            <Value active="True" name="st_e13"/>
            <Value active="True" name="st_e15"/>
            <Value active="True" name="st_e16"/>
            <Value active="True" name="st_e18"/>
            <Value active="True" name="st_e19"/>
            <Value active="True" name="st_e21"/>
            <Value active="True" name="st_e22"/>
            <Value active="True" name="st_e23"/>
            <Value active="True" name="st_e24"/>
            <Value active="True" name="st_e25"/>
            <Value active="True" name="st_e26"/>
            <Value active="True" name="st_e27"/>
            <Value active="True" name="st_e28"/>
            <Value active="True" name="st_e29"/>
            <Value active="True" name="st_e30"/>
            <Value active="True" name="st_e31"/>
            <Value active="True" name="st_e32"/>
            <Value active="True" name="st_e33"/>
            <Value active="True" name="st_e34"/>
            <Value active="True" name="st_e35"/>
            <Value active="True" name="st_e36"/>
            <Value active="True" name="st_e38"/>
            <Value active="True" name="st_e40"/>
            <Value active="True" name="st_e41"/>
            <Value active="True" name="st_e42"/>
            <Value active="True" name="st_fp7a"/>
            <Value active="True" name="st_fp7b"/>
            <Value active="True" name="st_fp7c"/>
            <Value active="True" name="st_fp7d"/>
            <Value active="True" name="st_fp7e"/>
            <Value active="True" name="st_fp8"/>
            <Value active="True" name="st_glmp_fp1"/>
            <Value active="True" name="st_glmp_fp2"/>
            <Value active="True" name="st_glmp_fp3"/>
            <Value active="True" name="st_glmp_kk90"/>
            <Value active="True" name="st_glmp_kk92"/>
            <Value active="True" name="st_glmp_kky"/>
            <Value active="True" name="st_glmp_ss1"/>
            <Value active="True" name="st_glmp_ss2"/>
            <Value active="True" name="st_ht"/>
            <Value active="True" name="st_iqpbk1"/>
            <Value active="True" name="st_iqpbk2"/>
            <Value active="True" name="st_jcbpaf2"/>
            <Value active="True" name="st_m1"/>
            <Value active="True" name="st_m2"/>
            <Value active="True" name="st_pan1"/>
            <Value active="True" name="st_ph1"/>
            <Value active="True" name="st_ph10"/>
            <Value active="True" name="st_ph11"/>
            <Value active="True" name="st_ph12"/>
            <Value active="True" name="st_ph13"/>
            <Value active="True" name="st_ph14"/>
            <Value active="True" name="st_ph15"/>
            <Value active="True" name="st_ph2"/>
            <Value active="True" name="st_ph20"/>
            <Value active="True" name="st_ph3"/>
            <Value active="True" name="st_phex"/>
            <Value active="True" name="st_qpc-m0"/>
            <Value active="True" name="st_qpc-m1"/>
            <Value active="True" name="st_qpc-m3a"/>
            <Value active="True" name="st_qpc-m3b"/>
            <Value active="True" name="st_qpc-m3c"/>
            <Value active="True" name="st_qpc-m4"/>
            <Value active="True" name="st_qpk1"/>
            <Value active="True" name="st_qpk2"/>
            <Value active="True" name="st_qpk3"/>
            <Value active="True" name="st_robot"/>
            <Value active="True" name="st_rv1"/>
            <Value active="True" name="st_rv2"/>
            <Value active="True" name="st_rv3"/>
            <Value active="True" name="st_rv7"/>
            <Value active="True" name="st_rv8"/>
            <Value active="True" name="st_rv9"/>
            <Value active="True" name="st_z"/>
            <Value active="True" name="steenbrf"/>
            <Value active="True" name="super1"/>
            <Value active="True" name="super2"/>
            <Value active="True" name="super3"/>
            <Value active="True" name="super3t"/>
            <Value active="True" name="supplychain"/>
            <Value active="True" name="supplychainp1_020306"/>
            <Value active="True" name="supplychainp1_022020"/>
            <Value active="True" name="supplychainp1_030510"/>
            <Value active="True" name="supplychainp1_053050"/>
            <Value active="True" name="supplychainr1_020306"/>
            <Value active="True" name="supplychainr1_022020"/>
            <Value active="True" name="supplychainr1_030510"/>
            <Value active="True" name="supplychainr1_053050"/>
            <Value active="True" name="synheat"/>
            <Value active="True" name="t1000"/>
            <Value active="True" name="tanksize"/>
            <Value active="True" name="telecomsp_metro"/>
            <Value active="True" name="telecomsp_njlata"/>
            <Value active="True" name="telecomsp_nor_sun"/>
            <Value active="True" name="telecomsp_pacbell"/>
            <Value active="True" name="tln12"/>
            <Value active="True" name="tln2"/>
            <Value active="True" name="tln4"/>
            <Value active="True" name="tln5"/>
            <Value active="True" name="tln6"/>
            <Value active="True" name="tln7"/>
            <Value active="True" name="tloss"/>
            <Value active="True" name="tltr"/>
            <Value active="True" name="topopt-cantilever_60x40_50"/>
            <Value active="True" name="topopt-mbb_60x40_50"/>
            <Value active="True" name="topopt-zhou-rozvany_75"/>
            <Value active="True" name="toroidal2g20_5555"/>
            <Value active="True" name="toroidal3g7_6666"/>
            <Value active="True" name="torsion100"/>
            <Value active="True" name="torsion25"/>
            <Value active="True" name="torsion50"/>
            <Value active="True" name="torsion75"/>
            <Value active="True" name="trainf"/>
            <Value active="True" name="transswitch0009p"/>
            <Value active="True" name="transswitch0009r"/>
            <Value active="True" name="transswitch0014p"/>
            <Value active="True" name="transswitch0014r"/>
            <Value active="True" name="transswitch0030p"/>
            <Value active="True" name="transswitch0030r"/>
            <Value active="True" name="transswitch0039p"/>
            <Value active="True" name="transswitch0039r"/>
            <Value active="True" name="transswitch0057p"/>
            <Value active="True" name="transswitch0057r"/>
            <Value active="True" name="transswitch0118p"/>
            <Value active="True" name="transswitch0118r"/>
            <Value active="True" name="transswitch0300p"/>
            <Value active="True" name="transswitch0300r"/>
            <Value active="True" name="transswitch2383wpp"/>
            <Value active="True" name="transswitch2383wpr"/>
            <Value active="True" name="transswitch2736spp"/>
            <Value active="True" name="transswitch2736spr"/>
            <Value active="True" name="tricp"/>
            <Value active="True" name="trigx"/>
            <Value active="True" name="truck"/>
            <Value active="True" name="tspn05"/>
            <Value active="True" name="tspn08"/>
            <Value active="True" name="tspn10"/>
            <Value active="True" name="tspn12"/>
            <Value active="True" name="tspn15"/>
            <Value active="True" name="unitcommit2"/>
            <Value active="True" name="unitcommit_200_0_5_mod_7"/>
            <Value active="True" name="unitcommit_200_100_2_mod_7"/>
            <Value active="True" name="uselinear"/>
            <Value active="True" name="util"/>
            <Value active="True" name="var_con10"/>
            <Value active="True" name="var_con5"/>
            <Value active="True" name="wager"/>
            <Value active="True" name="wall"/>
            <Value active="True" name="wallfix"/>
            <Value active="True" name="waste"/>
            <Value active="True" name="wastepaper3"/>
            <Value active="True" name="wastepaper4"/>
            <Value active="True" name="wastepaper5"/>
            <Value active="True" name="wastepaper6"/>
            <Value active="True" name="wastewater02m1"/>
            <Value active="True" name="wastewater02m2"/>
            <Value active="True" name="wastewater04m1"/>
            <Value active="True" name="wastewater04m2"/>
            <Value active="True" name="wastewater05m1"/>
            <Value active="True" name="wastewater05m2"/>
            <Value active="True" name="wastewater11m1"/>
            <Value active="True" name="wastewater11m2"/>
            <Value active="True" name="wastewater12m1"/>
            <Value active="True" name="wastewater12m2"/>
            <Value active="True" name="wastewater13m1"/>
            <Value active="True" name="wastewater13m2"/>
            <Value active="True" name="wastewater14m1"/>
            <Value active="True" name="wastewater14m2"/>
            <Value active="True" name="wastewater15m1"/>
            <Value active="True" name="wastewater15m2"/>
            <Value active="True" name="water"/>
            <Value active="True" name="water3"/>
            <Value active="True" name="water4"/>
            <Value active="True" name="waterful2"/>
            <Value active="True" name="waternd1"/>
            <Value active="True" name="waternd2"/>
            <Value active="True" name="waternd_blacksburg"/>
            <Value active="True" name="waternd_fossiron"/>
            <Value active="True" name="waternd_fosspoly0"/>
            <Value active="True" name="waternd_fosspoly1"/>
            <Value active="True" name="waternd_hanoi"/>
            <Value active="True" name="waternd_modena"/>
            <Value active="True" name="waternd_pescara"/>
            <Value active="True" name="waternd_shamir"/>
            <Value active="True" name="waterno1_01"/>
            <Value active="True" name="waterno1_02"/>
            <Value active="True" name="waterno1_03"/>
            <Value active="True" name="waterno1_04"/>
            <Value active="True" name="waterno1_06"/>
            <Value active="True" name="waterno1_09"/>
            <Value active="True" name="waterno1_12"/>
            <Value active="True" name="waterno1_18"/>
            <Value active="True" name="waterno1_24"/>
            <Value active="True" name="waterno2_01"/>
            <Value active="True" name="waterno2_02"/>
            <Value active="True" name="waterno2_03"/>
            <Value active="True" name="waterno2_04"/>
            <Value active="True" name="waterno2_06"/>
            <Value active="True" name="waterno2_09"/>
            <Value active="True" name="waterno2_12"/>
            <Value active="True" name="waterno2_18"/>
            <Value active="True" name="waterno2_24"/>
            <Value active="True" name="waters"/>
            <Value active="True" name="watersbp"/>
            <Value active="True" name="watersym1"/>
            <Value active="True" name="watersym2"/>
            <Value active="True" name="watertreatnd_conc"/>
            <Value active="True" name="watertreatnd_flow"/>
            <Value active="True" name="waterund01"/>
            <Value active="True" name="waterund08"/>
            <Value active="True" name="waterund11"/>
            <Value active="True" name="waterund14"/>
            <Value active="True" name="waterund17"/>
            <Value active="True" name="waterund18"/>
            <Value active="True" name="waterund22"/>
            <Value active="True" name="waterund25"/>
            <Value active="True" name="waterund27"/>
            <Value active="True" name="waterund28"/>
            <Value active="True" name="waterund32"/>
            <Value active="True" name="waterund36"/>
            <Value active="True" name="waterx"/>
            <Value active="True" name="waterz"/>
            <Value active="True" name="weapons"/>
            <Value active="True" name="windfac"/>
            <Value active="True" name="worst"/>
        </Filter>
    </FilterGroup>
    <FilterGroup active="True" filtertype="intersection" name="\\convex">
        <Filter anytestrun="all" expression1="_abort_" expression2="0" operator="eq"/>
        <Filter anytestrun="all" expression1="_fail_" expression2="0" operator="eq"/>
        <Filter active="True" anytestrun="all" datakey="ProblemName" operator="keep">
            <Value active="True" name="abel"/>
            <Value active="True" name="alan"/>
            <Value active="True" name="arki0001"/>
            <Value active="True" name="ball_mk2_10"/>
            <Value active="True" name="ball_mk2_30"/>
            <Value active="True" name="ball_mk3_10"/>
            <Value active="True" name="ball_mk3_20"/>
            <Value active="True" name="ball_mk3_30"/>
            <Value active="True" name="ball_mk4_05"/>
            <Value active="True" name="ball_mk4_10"/>
            <Value active="True" name="ball_mk4_15"/>
            <Value active="True" name="batch"/>
            <Value active="True" name="batch0812"/>
            <Value active="True" name="batchdes"/>
            <Value active="True" name="batchs101006m"/>
            <Value active="True" name="batchs121208m"/>
            <Value active="True" name="batchs151208m"/>
            <Value active="True" name="batchs201210m"/>
            <Value active="True" name="clay0203h"/>
            <Value active="True" name="clay0203m"/>
            <Value active="True" name="clay0204h"/>
            <Value active="True" name="clay0204m"/>
            <Value active="True" name="clay0205h"/>
            <Value active="True" name="clay0205m"/>
            <Value active="True" name="clay0303h"/>
            <Value active="True" name="clay0303m"/>
            <Value active="True" name="clay0304h"/>
            <Value active="True" name="clay0304m"/>
            <Value active="True" name="clay0305h"/>
            <Value active="True" name="clay0305m"/>
            <Value active="True" name="color_lab2_4x0"/>
            <Value active="True" name="color_lab6b_4x20"/>
            <Value active="True" name="cvxnonsep_normcon20"/>
            <Value active="True" name="cvxnonsep_normcon20r"/>
            <Value active="True" name="cvxnonsep_normcon30"/>
            <Value active="True" name="cvxnonsep_normcon30r"/>
            <Value active="True" name="cvxnonsep_normcon40"/>
            <Value active="True" name="cvxnonsep_normcon40r"/>
            <Value active="True" name="cvxnonsep_nsig20"/>
            <Value active="True" name="cvxnonsep_nsig20r"/>
            <Value active="True" name="cvxnonsep_nsig30"/>
            <Value active="True" name="cvxnonsep_nsig30r"/>
            <Value active="True" name="cvxnonsep_nsig40"/>
            <Value active="True" name="cvxnonsep_nsig40r"/>
            <Value active="True" name="cvxnonsep_pcon20"/>
            <Value active="True" name="cvxnonsep_pcon20r"/>
            <Value active="True" name="cvxnonsep_pcon30"/>
            <Value active="True" name="cvxnonsep_pcon30r"/>
            <Value active="True" name="cvxnonsep_pcon40"/>
            <Value active="True" name="cvxnonsep_pcon40r"/>
            <Value active="True" name="cvxnonsep_psig20"/>
            <Value active="True" name="cvxnonsep_psig20r"/>
            <Value active="True" name="cvxnonsep_psig30"/>
            <Value active="True" name="cvxnonsep_psig30r"/>
            <Value active="True" name="cvxnonsep_psig40"/>
            <Value active="True" name="cvxnonsep_psig40r"/>
            <Value active="True" name="du-opt"/>
            <Value active="True" name="du-opt5"/>
            <Value active="True" name="enpro48pb"/>
            <Value active="True" name="enpro56pb"/>
            <Value active="True" name="ex1223"/>
            <Value active="True" name="ex1223a"/>
            <Value active="True" name="ex1223b"/>
            <Value active="True" name="ex4"/>
            <Value active="True" name="fac1"/>
            <Value active="True" name="fac2"/>
            <Value active="True" name="fac3"/>
            <Value active="True" name="flay02h"/>
            <Value active="True" name="flay02m"/>
            <Value active="True" name="flay03h"/>
            <Value active="True" name="flay03m"/>
            <Value active="True" name="flay04h"/>
            <Value active="True" name="flay04m"/>
            <Value active="True" name="flay05h"/>
            <Value active="True" name="flay05m"/>
            <Value active="True" name="flay06h"/>
            <Value active="True" name="flay06m"/>
            <Value active="True" name="fo7"/>
            <Value active="True" name="fo7_2"/>
            <Value active="True" name="fo7_ar25_1"/>
            <Value active="True" name="fo7_ar2_1"/>
            <Value active="True" name="fo7_ar3_1"/>
            <Value active="True" name="fo7_ar4_1"/>
            <Value active="True" name="fo7_ar5_1"/>
            <Value active="True" name="fo8"/>
            <Value active="True" name="fo8_ar25_1"/>
            <Value active="True" name="fo8_ar2_1"/>
            <Value active="True" name="fo8_ar3_1"/>
            <Value active="True" name="fo8_ar4_1"/>
            <Value active="True" name="fo8_ar5_1"/>
            <Value active="True" name="fo9"/>
            <Value active="True" name="fo9_ar25_1"/>
            <Value active="True" name="fo9_ar2_1"/>
            <Value active="True" name="fo9_ar3_1"/>
            <Value active="True" name="fo9_ar4_1"/>
            <Value active="True" name="fo9_ar5_1"/>
            <Value active="True" name="gams01"/>
            <Value active="True" name="gbd"/>
            <Value active="True" name="gtm"/>
            <Value active="True" name="harker"/>
            <Value active="True" name="hybriddynamic_fixed"/>
            <Value active="True" name="ibs2"/>
            <Value active="True" name="immun"/>
            <Value active="True" name="jbearing100"/>
            <Value active="True" name="jbearing25"/>
            <Value active="True" name="jbearing50"/>
            <Value active="True" name="jbearing75"/>
            <Value active="True" name="jit1"/>
            <Value active="True" name="linear"/>
            <Value active="True" name="m3"/>
            <Value active="True" name="m6"/>
            <Value active="True" name="m7"/>
            <Value active="True" name="m7_ar25_1"/>
            <Value active="True" name="m7_ar2_1"/>
            <Value active="True" name="m7_ar3_1"/>
            <Value active="True" name="m7_ar4_1"/>
            <Value active="True" name="m7_ar5_1"/>
            <Value active="True" name="meanvar"/>
            <Value active="True" name="meanvar-orl400_05_e_8"/>
            <Value active="True" name="meanvarx"/>
            <Value active="True" name="meanvarxsc"/>
            <Value active="True" name="netmod_dol1"/>
            <Value active="True" name="netmod_dol2"/>
            <Value active="True" name="netmod_kar1"/>
            <Value active="True" name="netmod_kar2"/>
            <Value active="True" name="no7_ar25_1"/>
            <Value active="True" name="no7_ar2_1"/>
            <Value active="True" name="no7_ar3_1"/>
            <Value active="True" name="no7_ar4_1"/>
            <Value active="True" name="no7_ar5_1"/>
            <Value active="True" name="nvs03"/>
            <Value active="True" name="nvs10"/>
            <Value active="True" name="nvs11"/>
            <Value active="True" name="nvs12"/>
            <Value active="True" name="nvs15"/>
            <Value active="True" name="o7"/>
            <Value active="True" name="o7_2"/>
            <Value active="True" name="o7_ar25_1"/>
            <Value active="True" name="o7_ar2_1"/>
            <Value active="True" name="o7_ar3_1"/>
            <Value active="True" name="o7_ar4_1"/>
            <Value active="True" name="o7_ar5_1"/>
            <Value active="True" name="o8_ar4_1"/>
            <Value active="True" name="o9_ar4_1"/>
            <Value active="True" name="parabol5_2_1"/>
            <Value active="True" name="pedigree_ex1058"/>
            <Value active="True" name="pedigree_ex485"/>
            <Value active="True" name="pedigree_ex485_2"/>
            <Value active="True" name="pedigree_sim2000"/>
            <Value active="True" name="pedigree_sim400"/>
            <Value active="True" name="pedigree_sp_top4_250"/>
            <Value active="True" name="pedigree_sp_top4_300"/>
            <Value active="True" name="pedigree_sp_top4_350tr"/>
            <Value active="True" name="pedigree_sp_top5_200"/>
            <Value active="True" name="pedigree_sp_top5_250"/>
            <Value active="True" name="pollut"/>
            <Value active="True" name="portfol_buyin"/>
            <Value active="True" name="portfol_card"/>
            <Value active="True" name="portfol_classical050_1"/>
            <Value active="True" name="portfol_classical200_2"/>
            <Value active="True" name="portfol_roundlot"/>
            <Value active="True" name="procsyn"/>
            <Value active="True" name="procurement2mot"/>
            <Value active="True" name="qp2"/>
            <Value active="True" name="qp4"/>
            <Value active="True" name="ravempb"/>
            <Value active="True" name="risk2bpb"/>
            <Value active="True" name="rsyn0805h"/>
            <Value active="True" name="rsyn0805m"/>
            <Value active="True" name="rsyn0805m02h"/>
            <Value active="True" name="rsyn0805m02m"/>
            <Value active="True" name="rsyn0805m03h"/>
            <Value active="True" name="rsyn0805m03m"/>
            <Value active="True" name="rsyn0805m04h"/>
            <Value active="True" name="rsyn0805m04m"/>
            <Value active="True" name="rsyn0810h"/>
            <Value active="True" name="rsyn0810m"/>
            <Value active="True" name="rsyn0810m02h"/>
            <Value active="True" name="rsyn0810m02m"/>
            <Value active="True" name="rsyn0810m03h"/>
            <Value active="True" name="rsyn0810m03m"/>
            <Value active="True" name="rsyn0810m04h"/>
            <Value active="True" name="rsyn0810m04m"/>
            <Value active="True" name="rsyn0815h"/>
            <Value active="True" name="rsyn0815m"/>
            <Value active="True" name="rsyn0815m02h"/>
            <Value active="True" name="rsyn0815m02m"/>
            <Value active="True" name="rsyn0815m03h"/>
            <Value active="True" name="rsyn0815m03m"/>
            <Value active="True" name="rsyn0815m04h"/>
            <Value active="True" name="rsyn0815m04m"/>
            <Value active="True" name="rsyn0820h"/>
            <Value active="True" name="rsyn0820m"/>
            <Value active="True" name="rsyn0820m02h"/>
            <Value active="True" name="rsyn0820m02m"/>
            <Value active="True" name="rsyn0820m03h"/>
            <Value active="True" name="rsyn0820m03m"/>
            <Value active="True" name="rsyn0820m04h"/>
            <Value active="True" name="rsyn0820m04m"/>
            <Value active="True" name="rsyn0830h"/>
            <Value active="True" name="rsyn0830m"/>
            <Value active="True" name="rsyn0830m02h"/>
            <Value active="True" name="rsyn0830m02m"/>
            <Value active="True" name="rsyn0830m03h"/>
            <Value active="True" name="rsyn0830m03m"/>
            <Value active="True" name="rsyn0830m04h"/>
            <Value active="True" name="rsyn0830m04m"/>
            <Value active="True" name="rsyn0840h"/>
            <Value active="True" name="rsyn0840m"/>
            <Value active="True" name="rsyn0840m02h"/>
            <Value active="True" name="rsyn0840m02m"/>
            <Value active="True" name="rsyn0840m03h"/>
            <Value active="True" name="rsyn0840m03m"/>
            <Value active="True" name="rsyn0840m04h"/>
            <Value active="True" name="rsyn0840m04m"/>
            <Value active="True" name="sambal"/>
            <Value active="True" name="sample"/>
            <Value active="True" name="slay04h"/>
            <Value active="True" name="slay04m"/>
            <Value active="True" name="slay05h"/>
            <Value active="True" name="slay05m"/>
            <Value active="True" name="slay06h"/>
            <Value active="True" name="slay06m"/>
            <Value active="True" name="slay07h"/>
            <Value active="True" name="slay07m"/>
            <Value active="True" name="slay08h"/>
            <Value active="True" name="slay08m"/>
            <Value active="True" name="slay09h"/>
            <Value active="True" name="slay09m"/>
            <Value active="True" name="slay10h"/>
            <Value active="True" name="slay10m"/>
            <Value active="True" name="smallinvDAXr1b010-011"/>
            <Value active="True" name="smallinvDAXr1b020-022"/>
            <Value active="True" name="smallinvDAXr1b050-055"/>
            <Value active="True" name="smallinvDAXr1b100-110"/>
            <Value active="True" name="smallinvDAXr1b150-165"/>
            <Value active="True" name="smallinvDAXr1b200-220"/>
            <Value active="True" name="smallinvDAXr2b010-011"/>
            <Value active="True" name="smallinvDAXr2b020-022"/>
            <Value active="True" name="smallinvDAXr2b050-055"/>
            <Value active="True" name="smallinvDAXr2b100-110"/>
            <Value active="True" name="smallinvDAXr2b150-165"/>
            <Value active="True" name="smallinvDAXr2b200-220"/>
            <Value active="True" name="smallinvDAXr3b010-011"/>
            <Value active="True" name="smallinvDAXr3b020-022"/>
            <Value active="True" name="smallinvDAXr3b050-055"/>
            <Value active="True" name="smallinvDAXr3b100-110"/>
            <Value active="True" name="smallinvDAXr3b150-165"/>
            <Value active="True" name="smallinvDAXr3b200-220"/>
            <Value active="True" name="smallinvDAXr4b010-011"/>
            <Value active="True" name="smallinvDAXr4b020-022"/>
            <Value active="True" name="smallinvDAXr4b050-055"/>
            <Value active="True" name="smallinvDAXr4b100-110"/>
            <Value active="True" name="smallinvDAXr4b150-165"/>
            <Value active="True" name="smallinvDAXr4b200-220"/>
            <Value active="True" name="smallinvDAXr5b010-011"/>
            <Value active="True" name="smallinvDAXr5b020-022"/>
            <Value active="True" name="smallinvDAXr5b050-055"/>
            <Value active="True" name="smallinvDAXr5b100-110"/>
            <Value active="True" name="smallinvDAXr5b150-165"/>
            <Value active="True" name="smallinvDAXr5b200-220"/>
            <Value active="True" name="squfl010-025"/>
            <Value active="True" name="squfl010-040"/>
            <Value active="True" name="squfl010-080"/>
            <Value active="True" name="squfl015-060"/>
            <Value active="True" name="squfl015-080"/>
            <Value active="True" name="squfl020-040"/>
            <Value active="True" name="squfl020-050"/>
            <Value active="True" name="squfl020-150"/>
            <Value active="True" name="squfl025-025"/>
            <Value active="True" name="squfl025-030"/>
            <Value active="True" name="squfl025-040"/>
            <Value active="True" name="squfl030-100"/>
            <Value active="True" name="squfl030-150"/>
            <Value active="True" name="squfl040-080"/>
            <Value active="True" name="srcpm"/>
            <Value active="True" name="sssd08-04"/>
            <Value active="True" name="sssd12-05"/>
            <Value active="True" name="sssd15-04"/>
            <Value active="True" name="sssd15-06"/>
            <Value active="True" name="sssd15-08"/>
            <Value active="True" name="sssd16-07"/>
            <Value active="True" name="sssd18-06"/>
            <Value active="True" name="sssd18-08"/>
            <Value active="True" name="sssd20-04"/>
            <Value active="True" name="sssd20-08"/>
            <Value active="True" name="sssd22-08"/>
            <Value active="True" name="sssd25-04"/>
            <Value active="True" name="sssd25-08"/>
            <Value active="True" name="st_cqpf"/>
            <Value active="True" name="st_cqpjk1"/>
            <Value active="True" name="st_cqpjk2"/>
            <Value active="True" name="st_e14"/>
            <Value active="True" name="st_e17"/>
            <Value active="True" name="st_miqp1"/>
            <Value active="True" name="st_miqp2"/>
            <Value active="True" name="st_miqp3"/>
            <Value active="True" name="st_miqp4"/>
            <Value active="True" name="st_miqp5"/>
            <Value active="True" name="st_test1"/>
            <Value active="True" name="st_test2"/>
            <Value active="True" name="st_test3"/>
            <Value active="True" name="st_test4"/>
            <Value active="True" name="st_test5"/>
            <Value active="True" name="st_test6"/>
            <Value active="True" name="st_test8"/>
            <Value active="True" name="st_testgr1"/>
            <Value active="True" name="st_testgr3"/>
            <Value active="True" name="st_testph4"/>
            <Value active="True" name="stockcycle"/>
            <Value active="True" name="syn05h"/>
            <Value active="True" name="syn05m"/>
            <Value active="True" name="syn05m02h"/>
            <Value active="True" name="syn05m02m"/>
            <Value active="True" name="syn05m03h"/>
            <Value active="True" name="syn05m03m"/>
            <Value active="True" name="syn05m04h"/>
            <Value active="True" name="syn05m04m"/>
            <Value active="True" name="syn10h"/>
            <Value active="True" name="syn10m"/>
            <Value active="True" name="syn10m02h"/>
            <Value active="True" name="syn10m02m"/>
            <Value active="True" name="syn10m03h"/>
            <Value active="True" name="syn10m03m"/>
            <Value active="True" name="syn10m04h"/>
            <Value active="True" name="syn10m04m"/>
            <Value active="True" name="syn15h"/>
            <Value active="True" name="syn15m"/>
            <Value active="True" name="syn15m02h"/>
            <Value active="True" name="syn15m02m"/>
            <Value active="True" name="syn15m03h"/>
            <Value active="True" name="syn15m03m"/>
            <Value active="True" name="syn15m04h"/>
            <Value active="True" name="syn15m04m"/>
            <Value active="True" name="syn20h"/>
            <Value active="True" name="syn20m"/>
            <Value active="True" name="syn20m02h"/>
            <Value active="True" name="syn20m02m"/>
            <Value active="True" name="syn20m03h"/>
            <Value active="True" name="syn20m03m"/>
            <Value active="True" name="syn20m04h"/>
            <Value active="True" name="syn20m04m"/>
            <Value active="True" name="syn30h"/>
            <Value active="True" name="syn30m"/>
            <Value active="True" name="syn30m02h"/>
            <Value active="True" name="syn30m02m"/>
            <Value active="True" name="syn30m03h"/>
            <Value active="True" name="syn30m03m"/>
            <Value active="True" name="syn30m04h"/>
            <Value active="True" name="syn30m04m"/>
            <Value active="True" name="syn40h"/>
            <Value active="True" name="syn40m"/>
            <Value active="True" name="syn40m02h"/>
            <Value active="True" name="syn40m02m"/>
            <Value active="True" name="syn40m03h"/>
            <Value active="True" name="syn40m03m"/>
            <Value active="True" name="syn40m04h"/>
            <Value active="True" name="syn40m04m"/>
            <Value active="True" name="synthes1"/>
            <Value active="True" name="synthes2"/>
            <Value active="True" name="synthes3"/>
            <Value active="True" name="tls12"/>
            <Value active="True" name="tls2"/>
            <Value active="True" name="tls4"/>
            <Value active="True" name="tls5"/>
            <Value active="True" name="tls6"/>
            <Value active="True" name="tls7"/>
            <Value active="True" name="turkey"/>
            <Value active="True" name="unitcommit1"/>
            <Value active="True" name="unitcommit_200_100_1_mod_8"/>
            <Value active="True" name="unitcommit_200_100_2_mod_8"/>
            <Value active="True" name="unitcommit_50_20_2_mod_8"/>
            <Value active="True" name="watercontamination0202"/>
            <Value active="True" name="watercontamination0202r"/>
            <Value active="True" name="watercontamination0303"/>
            <Value active="True" name="watercontamination0303r"/>
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
        droplist = self.get_argument("droplist")

        # read testrunids
        testrun_ids = self.get_argument("testruns")
        testrunids = testrun_ids.split(",")

        # read defaultgroup
        default_id = self.get_argument("default", testrunids[0])

        # get testruns and default
        testruns = get_testruns(testrunids)

        # evaluate with ipet
        ex, excluded_inst = setup_experiment(testruns, droplist)
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

            # ipetlogger.removeHandler(rbhandler)
            rbhandler.close()

            # postprocessing
            html_long = process_ipet_table(html_long, {**repres["short"], **repres["all"]},
                    add_ind=False, swap=True)
            html_agg = process_ipet_table(html_agg, {**repres["long"], **repres["all"]},
                    add_ind=True, swap=False)

            message = ", ".join(sorted(list(set(excluded_inst))))
            print(message)
            # render to strings
            html_tables = self.render_string("results/evaluation.html",
                    ipet_long_table=html_long,
                    ipet_aggregated_table=html_agg,
                    columns=cols_dict,
                    psmessage=message).decode("utf-8")

            # send evaluated data
            mydict = {"rb-ipet-eval-result": html_tables,
                      "rb-ipet-buttons": fg_buttons_str}
            response = json.dumps(mydict)
            self.write(response)
            self.flush()


        elif style == "latex":
            if aggtable.empty:
                self.write_error(status_code=204, msg="Sorry, aggregated table is empty. Aborting.")
                self.flush()
                return

            # generate a table that can be used in the release-report
            df = aggtable
            # care for the columns
            df = df.reset_index()
            poss = ['RubberbandId', 'GitHash', 'Settings', 'LPSolver']
            for i in poss:
                if i in df.columns:
                    colindex = i
                    break

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
                    '\\convex', '\\nonconvex', '\miplib~2017', '\coral', 'continuous', 'integer']

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


def setup_experiment(testruns, droplist=""):
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

    regexlist = []
    for x in droplist.split(","):
        x = x.strip()
        # defaultvalue, if empty we don't want to exclude everything
        if x == "":
            continue
        try:
            y = re.compile(x)
            regexlist.append(y)
        except:
            pass

    excluded_inst = []
    # get data
    for t in testruns:
        # update representation
        additional_data = {"RubberbandId": get_rbid_representation(t, "extended")}

        # collect data and pass to ipet
        ipettestrun = TestRun()
        tr_raw_data = t.get_data(add_data=additional_data)

        tr_data = {}
        for i in tr_raw_data.keys():
            for r in regexlist:
                if r.match(i):
                    excluded_inst.append(i)
                    break
            else:
                tr_data[i] = tr_raw_data[i]

        ipettestrun.data = pd.DataFrame(tr_data).T

        ex.testruns.append(ipettestrun)
    return ex, excluded_inst


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
