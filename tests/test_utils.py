import os.path
import yaml
import json

from ipet_reader import Experiment
from rubberband.utils import generate_sha256_hash
from rubberband.utils.importer import _determine_type

DATAFILES = "data/check.IP_1s_1m.scip-3.2.1.linux.x86_64.gnu.dbg.cpx.opt-low.default.out"
FULLDATAPATH = os.path.join(os.path.dirname(__file__), DATAFILES)


def test_hasher_file():
    expected_result = "0a8c44c1b6f4e7e7f595c6fbaab804832d3c8daa3cbf516eb33064f200533327"
    computed_hash = generate_sha256_hash(FULLDATAPATH)
    assert computed_hash == expected_result


def test_hasher_none():
    computed_hash = generate_sha256_hash(FULLDATAPATH.replace(".out", ".fake"))
    assert computed_hash is None


def test_determine_type():
    file_base = os.path.join(os.path.dirname(__file__), "data",
        "check.short.scip-4.0.0.linux.x86_64.gnu.dbg.spx2.none.opt-low.default")
    c = Experiment()
    c.addOutputFile(file_base + ".out")
    c.addOutputFile(file_base + ".set")
    c.addOutputFile(file_base + ".err")
    c.collectData()
    manageables = c.testrunmanager.getManageables()[0]

    data = json.loads(manageables.data.to_json())
    results = {}
    instances = data["Nodes"].keys()

    for i in instances:
        results[i] = {"instance_name": i}

    for k, v in data.items():
        for instance, metric in v.items():
            k = k.replace(".", "_")
            results[instance][k] = metric

    for k, v in results.items():
        results[k]["instance_type"] = _determine_type(v)

    with open(file_base + ".yml") as f:
        compare_data = yaml.load(f)

    for d in compare_data:
        assert results[d]["instance_type"] == compare_data[d]
