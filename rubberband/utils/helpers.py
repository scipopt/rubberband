"""Collection of helper functions."""

from datetime import datetime
import os
import re
import string

from rubberband.constants import FORMAT_DATETIME_SHORT, FORMAT_DATETIME_LONG

# the -s<seed> appendix of a testrun filename, the only part that differs
# between the seeds of one build
SEED_APPENDIX = re.compile(r"-s\d+$")


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
    return """<span class="d-none d-xl-block">{longtext}</span>
    <span class="d-block d-xl-none" title="{longtext}">{shorttext}</span>
    """.format(longtext=text, shorttext=short)


def get_link(href, text, length=30, end=10):
    """Get a link with shortened text to href and full text as title."""
    link = '<a href="{}" title="{}">{}</a>'.format(
        href, text, shorten_str(text, length, end)
    )
    return link


def shorten_str(string, length=30, end=10):
    """Shorten a string to the given length."""
    if string is None:
        return ""
    if len(string) <= length:
        return string
    else:
        return "{}...{}".format(string[: length - end], string[-end:])


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
    Identify the build a testrun belongs to, so its seeds can be grouped.

    Testruns of one build differ only in their seed, and their filenames only in
    the ``-s<seed>`` appendix of
    ``check.<testset>.<binary>.<queue>.<setting>-s<seed>.out``. The binary
    carries the build date, so testruns built on different days keep different
    keys; the upload date is part of the key as well, both to separate reruns of
    the same build and because the older naming has no seed in the filename at
    all.

    Parameters
    ----------
    testrun : TestSet
        the testrun to place in a group

    Returns
    -------
    str
        key shared by exactly the testruns of one build
    """
    filename = getattr(testrun, "filename", "") or ""
    stem = SEED_APPENDIX.sub("", os.path.splitext(filename)[0])
    uploaded = str(getattr(testrun, "upload_timestamp", "") or "")[:10]

    return "{}|{}".format(stem, uploaded)


def build_groups(testruns):
    """
    Group testruns by build, for the seed grouping in the testrun tables.

    Parameters
    ----------
    testruns : list
        the testruns of one table, in the order they are rendered

    Returns
    -------
    dict
        testrun id -> {"key", "size", "parity"}, where size is the number of
        seeds in the group and parity alternates between neighbouring groups so
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
    Order testruns so that the seeds of one build sit next to each other.

    Builds keep the order they already had - the search sorts by date, so the
    most recent build stays on top - and within a build the seeds are ordered by
    seed number. Without this the seeds of two builds uploaded in the same batch
    end up interleaved and the group is impossible to see.

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
        key=lambda t: (order[build_group_key(t)], getattr(t, "seed", None) or 0),
    )


def rb_join_arg(li=[], identif="default", pos=0):
    """Construct url argument with identifier and li as list."""
    if li == []:
        return ""
    if pos == 0:
        letter = "?"
    else:
        letter = "&"
    return "{letter}{ident}={arg}".format(
        letter=letter, ident=identif, arg=",".join(li)
    )
