import os.path
from rubberband.utils import generate_sha256_hash

DATAFILES = (
    "data/check.IP_1s_1m.scip-3.2.1.linux.x86_64.gnu.dbg.cpx.opt-low.default.out"
)
FULLDATAPATH = os.path.join(os.path.dirname(__file__), DATAFILES)


def test_hasher_file():
    expected_result = "952a91b64de0b3cca2f520da5083624cf29d948d9058b34c71ef7fe839246065"
    computed_hash = generate_sha256_hash(FULLDATAPATH)
    assert computed_hash == expected_result


def test_hasher_none():
    computed_hash = generate_sha256_hash(FULLDATAPATH.replace(".out", ".fake"))
    assert computed_hash is None
