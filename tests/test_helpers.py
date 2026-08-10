from rubberband.utils.helpers import build_group_key, build_groups, group_testruns

BINARY = "check.mipdev3-solvable.scipoptspx_master_20260620.C6520.default"

# the metadata a run is uploaded with, as written by the check script
METADATA = {
    "Permutation": "0",
    "Seed": "0",
    "Settings": "default",
    "TstName": "mipdev3-solvable",
    "BinName": "scipoptspx_master_20260620/bin/scip",
    "NodeLimit": "2100000000",
    "MemLimit": "25000",
    "Threads": "1",
    "FeasTol": "default",
    "Queue": "C6520",
    "Exclusive": "--exclusive",
}


class FakeTestRun:
    """Stands in for a TestSet document, with the fields the grouping reads."""

    def __init__(self, filename, seed=0, permutation=0, metadata=None, uploaded="2026-07-24T19:53:00", **overrides):
        self.filename = filename
        self.seed = seed
        self.permutation = permutation
        self.upload_timestamp = uploaded
        self.meta = type("meta", (), {"id": filename})

        if metadata is None:
            metadata = dict(METADATA, Seed=str(seed), Permutation=str(permutation), **overrides)
        self.metadata = metadata


def test_seeds_of_one_build_share_a_key():
    plain = FakeTestRun(BINARY + ".out")
    seeded = FakeTestRun(BINARY + "-s2.out", seed=2)

    assert build_group_key(plain) == build_group_key(seeded)


def test_permutations_of_one_build_share_a_key():
    plain = FakeTestRun(BINARY + ".out")
    permuted = FakeTestRun(BINARY + "-p1.out", permutation=1)
    both = FakeTestRun(BINARY + "-p1-s2.out", permutation=1, seed=2)

    assert build_group_key(plain) == build_group_key(permuted)
    assert build_group_key(plain) == build_group_key(both)


def test_the_key_ignores_how_the_binary_was_reached():
    run = FakeTestRun(BINARY + ".out")
    from_elsewhere = FakeTestRun(BINARY + "-s1.out", seed=1, BinName="../scipoptspx_master_20260620/bin/scip")

    assert build_group_key(run) == build_group_key(from_elsewhere)


def test_anything_else_in_the_metadata_makes_another_build():
    run = FakeTestRun(BINARY + ".out")

    for field, value in [
        ("Settings", "SCIP-4202"),
        ("TstName", "mipdev3-complete"),
        ("BinName", "scipoptspx_master_202608081355/bin/scip"),
        ("Queue", "M640v2"),
        ("MemLimit", "50000"),
        ("Threads", "4"),
    ]:
        other = FakeTestRun(BINARY + ".out", **{field: value})
        assert build_group_key(run) != build_group_key(other), field


def test_runs_without_a_meta_file_fall_back_to_the_filename():
    # historical uploads have no metadata at all
    plain = FakeTestRun(BINARY + ".out", metadata={})
    seeded = FakeTestRun(BINARY + "-s2.out", seed=2, metadata={})
    other_day = FakeTestRun(BINARY + ".out", metadata={}, uploaded="2026-07-25T08:00:00")

    assert build_group_key(plain) == build_group_key(seeded)
    assert build_group_key(plain) != build_group_key(other_day)


def test_runs_are_grouped_and_ordered_by_permutation_and_seed():
    runs = [
        FakeTestRun(BINARY + "-p1-s1.out", seed=1, permutation=1),
        FakeTestRun(BINARY + ".other.out", Settings="other"),
        FakeTestRun(BINARY + ".out"),
        FakeTestRun(BINARY + "-s1.out", seed=1),
    ]

    ordered = group_testruns(runs)
    groups = build_groups(ordered)

    # the three runs of the build stay together, ordered by permutation then
    # seed, and the group keeps the place its first run had
    assert [r.filename for r in ordered] == [
        BINARY + ".out",
        BINARY + "-s1.out",
        BINARY + "-p1-s1.out",
        BINARY + ".other.out",
    ]

    sizes = {r.filename: groups[r.meta.id]["size"] for r in ordered}
    assert sizes[BINARY + ".out"] == 3
    assert sizes[BINARY + ".other.out"] == 1

    # the tree is drawn from the first and last run of a group
    assert groups[(BINARY + ".out")]["leads"] is True
    assert groups[(BINARY + "-p1-s1.out")]["last"] is True
