from rubberband.utils.helpers import build_group_key, build_groups, group_testruns

BINARY = "check.mipdev3-solvable.scipoptspx_master_20260620.C6520.default"


class FakeTestRun:
    """Stands in for a TestSet document, with the fields the grouping reads."""

    def __init__(self, filename, seed=0, permutation=0, uploaded="2026-07-24T19:53:00"):
        self.filename = filename
        self.seed = seed
        self.permutation = permutation
        self.upload_timestamp = uploaded
        self.meta = type("meta", (), {"id": filename})


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


def test_other_builds_and_dates_keep_their_own_key():
    run = FakeTestRun(BINARY + "-s1.out", seed=1)
    other_setting = FakeTestRun(
        "check.mipdev3-solvable.scipoptspx_master_20260620.C6520.SCIP-4202-s1.out", seed=1
    )
    other_build = FakeTestRun(
        "check.mipdev3-solvable.scipoptspx_master_20260624.C6520.default-s1.out", seed=1
    )
    other_day = FakeTestRun(BINARY + "-s1.out", seed=1, uploaded="2026-07-25T08:00:00")

    for different in (other_setting, other_build, other_day):
        assert build_group_key(run) != build_group_key(different)


def test_a_setting_ending_in_an_appendix_is_not_stripped():
    # the appendices are removed by the testrun's own seed and permutation, so a
    # setting that merely looks like one survives
    run = FakeTestRun("check.short.scip_master_20260620.C6520.heur-p1.out")

    assert build_group_key(run).startswith("check.short.scip_master_20260620.C6520.heur-p1")


def test_runs_are_grouped_and_ordered_by_permutation_and_seed():
    runs = [
        FakeTestRun(BINARY + "-p1-s1.out", seed=1, permutation=1),
        FakeTestRun("check.mipdev3-solvable.scipoptspx_master_20260620.C6520.other.out"),
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
        "check.mipdev3-solvable.scipoptspx_master_20260620.C6520.other.out",
    ]

    sizes = {r.filename: groups[r.meta.id]["size"] for r in ordered}
    assert sizes[BINARY + ".out"] == 3
    assert sizes["check.mipdev3-solvable.scipoptspx_master_20260620.C6520.other.out"] == 1

    # the tree is drawn from the first and last run of a group
    assert groups[(BINARY + ".out")]["leads"] is True
    assert groups[(BINARY + "-p1-s1.out")]["last"] is True
