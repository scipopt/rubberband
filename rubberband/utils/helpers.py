"""Collection of helper functions."""

import os
import re
import string
from datetime import datetime

from rubberband.constants import FORMAT_DATETIME_LONG, FORMAT_DATETIME_SHORT

# what the runs of one build differ in; everything else a run was uploaded with
# describes the build itself
GROUP_VARYING_METADATA = ("Seed", "Permutation", "uploader", "upload_timestamp")


def _run_metadata(testrun):
    """Return the uploaded metadata of a testrun as a plain dict."""
    metadata = getattr(testrun, "metadata", None)
    if metadata is None:
        return {}

    if hasattr(metadata, "to_dict"):
        metadata = metadata.to_dict()

    try:
        return dict(metadata)
    except (TypeError, ValueError):
        return {}


def _strip_run_appendices(stem, testrun):
    """
    Drop the -p<permutation> and -s<seed> appendices from a filename stem.

    The values of the testrun itself are used rather than a generic pattern, so
    a setting that happens to end in something like "-p1" is left alone. Both
    orders are handled, since only the check scripts decide which comes last.
    """
    for _ in range(2):
        for letter, attr in (("s", "seed"), ("p", "permutation")):
            value = getattr(testrun, attr, None)
            if value:
                stem = re.sub(rf"-{letter}{int(value)}$", "", stem)

    return stem


def shortening_repres_id(repres, key):
    """
    Shorten a span containing 'representation' with full text saved under attribute 'key'.

    Get a shortening span where the text is under key in dicts repres['long'] and repres['short'].
    """
    return shortening_span(repres["long"][key], repres["short"][key])


def shortening_span(text, short):
    """
    Get a span with text that shortenes itself on small screens.

    For example used in column headers.
    """
    return f"""<span class="d-none d-xl-block">{text}</span>
    <span class="d-block d-xl-none" title="{text}">{short}</span>
    """


def get_link(href, text, length=30, end=10):
    """Get a link with shortened text to href and full text as title."""
    link = f'<a href="{href}" title="{text}">{shorten_str(text, length, end)}</a>'
    return link


def shorten_str(string, length=30, end=10):
    """Shorten a string to the given length."""
    if string is None:
        return ""
    if len(string) <= length:
        return string
    else:
        return f"{string[: length - end]}...{string[-end:]}"


def get_letters_list(quantity):
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


def get_rbid_representation(testrun, mode="extended"):
    """
    Get representative string for a testrun.

    This is used for uniqueness and sorting

    Parameters
    ----------
    testrun : rubberband.TestSet
        TestSet to be represented
    mode : str
        ["extended", "readable"] format of representative

    Returns
    -------
    str
        representation
    """
    setshort = testrun.settings_short_name
    if setshort is None:
        setshort = ""

    ts = ""
    ts_time = ""
    if testrun.git_commit_timestamp:
        ts = (
            "("
            + datetime.strftime(testrun.git_commit_timestamp, FORMAT_DATETIME_SHORT)
            + ")"
        )
        ts_time = datetime.strftime(testrun.git_commit_timestamp, "%Y%m%d%H%M%S")

    if mode == "readable":
        rbid_repres = " " + shorten_str(setshort, 15, 5) + " " + ts
    else:  # if mode == "extended"
        rbid_repres = ts_time + setshort + testrun.id

    return rbid_repres


def setup_testruns_subst_dict(testruns):
    """
    Setup the substitutions dictionary for the regular view.

    Parameters
    ----------
    testruns : list
        a list of rubberband TestSet

    Returns
    -------
    dict
        dictionary of representation key value pairs
    """
    # get representations letters
    letters = get_letters_list(len(testruns))

    # for long table (short subst), for aggregated (long) and for all "all"
    repres = {"long": {}, "short": {}, "all": {}}

    # substitutions in both tables
    repres["all"]["GitHash"] = "Commit"

    for tr in testruns:
        # add representation for githash: timestamp of commit
        if tr.git_commit_timestamp:
            ts = (
                "("
                + datetime.strftime(tr.git_commit_timestamp, FORMAT_DATETIME_LONG)
                + ")"
            )
            repres["all"][tr.git_hash] = ts

        extended_rbid = get_rbid_representation(tr, "extended")
        readable_rbid = get_rbid_representation(tr, "readable")

        repres["long"][extended_rbid] = readable_rbid
        repres["all"][extended_rbid] = tr.id

    count = 0

    # sort testruns by extended_rbid
    for extended_rbid in sorted(repres["long"].keys()):
        tid = repres["all"][extended_rbid]

        # prepend a letter to the readable_rbid
        longname = letters[count] + repres["long"][extended_rbid]

        # substitute the extended_rbids with a sortable and readable name for ipet tables
        repres["short"][extended_rbid] = letters[count]
        repres["long"][extended_rbid] = longname

        # in the template file we need the testrun id as a key
        repres["short"][tid] = letters[count]
        repres["long"][tid] = longname

        # count through the letters of the alphabet
        count = count + 1
    return repres


def build_group_key(testrun):
    """
    Identify the build a testrun belongs to, so its runs can be grouped.

    A run is uploaded with the metadata of the check script - ``TstName``,
    ``BinName``, ``Settings``, ``Queue``, the limits, and so on - of which only
    ``Seed`` and ``Permutation`` differ between the runs of one build. Everything
    else taken together is the build, so that is the key. ``BinName`` carries the
    date and time the binary was built, which keeps separate builds apart on its
    own.

    Testruns uploaded without a meta file have no such metadata; they fall back
    to their filename with the ``-p<permutation>`` and ``-s<seed>`` appendices
    removed, plus the upload date to keep separate uploads apart.

    Parameters
    ----------
    testrun : TestSet
        the testrun to place in a group

    Returns
    -------
    str
        key shared by exactly the testruns of one build
    """
    metadata = _run_metadata(testrun)
    build = {k: v for k, v in metadata.items() if k not in GROUP_VARYING_METADATA}

    if build:
        # the same binary is referred to both as "<build>/bin/scip" and
        # "../<build>/bin/scip", depending on where the check ran from
        if build.get("BinName"):
            build["BinName"] = re.sub(r"^(\.\.?/)+", "", str(build["BinName"]))
        return "|".join(f"{key}={build[key]}" for key in sorted(build))

    filename = getattr(testrun, "filename", "") or ""
    stem = _strip_run_appendices(os.path.splitext(filename)[0], testrun)
    uploaded = str(getattr(testrun, "upload_timestamp", "") or "")[:10]

    return f"{stem}|{uploaded}"


def build_groups(testruns):
    """
    Group testruns by build, for the grouping in the testrun tables.

    Parameters
    ----------
    testruns : list
        the testruns of one table, in the order they are rendered

    Returns
    -------
    dict
        testrun id -> {"key", "size", "parity"}, where size is the number of
        runs in the group and parity alternates between neighbouring groups so
        they can be told apart visually
    """
    keys = {}
    sizes = {}
    for testrun in testruns or []:
        key = build_group_key(testrun)
        keys[testrun.meta.id] = key
        sizes[key] = sizes.get(key, 0) + 1

    parities = {}
    leaders = {}
    last = {}
    for tid, key in keys.items():
        if key not in parities:
            parities[key] = len(parities) % 2
            leaders[key] = tid
        last[key] = tid

    return {
        tid: {
            "key": key,
            "size": sizes[key],
            "parity": parities[key],
            # only the first testrun of a group carries the group checkbox, so
            # there is never a second, ambiguous checkbox on a row
            "leads": leaders[key] == tid,
            # first and last are drawn with the corners of the tree
            "last": last[key] == tid,
        }
        for tid, key in keys.items()
    }


def group_testruns(testruns):
    """
    Order testruns so that the runs of one build sit next to each other.

    Builds keep the order they already had - the search sorts by date, so the
    most recent build stays on top - and within a build the runs are ordered by
    permutation and seed. Without this the runs of two builds uploaded in the
    same batch end up interleaved and the group is impossible to see.

    Parameters
    ----------
    testruns : list
        the testruns of one table

    Returns
    -------
    list
        the same testruns, grouped by build
    """
    if not testruns:
        return testruns

    order = {}
    for testrun in testruns:
        order.setdefault(build_group_key(testrun), len(order))

    return sorted(
        testruns,
        key=lambda t: (
            order[build_group_key(t)],
            getattr(t, "permutation", None) or 0,
            getattr(t, "seed", None) or 0,
        ),
    )


def rb_join_arg(li=None, identif="default", pos=0):
    """Construct url argument with identifier and li as list."""
    if li is None or li == []:
        return ""
    if pos == 0:
        letter = "?"
    else:
        letter = "&"
    return "{letter}{ident}={arg}".format(
        letter=letter, ident=identif, arg=",".join(li)
    )
