"""Common methods for request handlers."""
from rubberband.models import TestSet


def search(query):
    """
    Execute a search to elasticsearch database, gives by default the 100 first results.

    Parameters
    ----------
    query : dict
        Search parameters

    Results
    -------
    Response
        elasticsearch-dsl Response object
    """
    s = TestSet.search()

    if "tags" in query:
        tags = query["tags"]
        tags = tags.split(",")
        tags = list(map(str.strip, tags))
        s = s.filter("terms", tags=tags)
        del(query["tags"])

    # return 100 items unless a limit is explicitly set
    limit = query.pop("limit", None) or 100
    limit = int(limit)

    for field, value in query.items():
        if not field == "git_hash":
            filter_dict = {field: value}
            s = s.filter("term", **filter_dict)
        else:
            filter_dict = {"default_field": field, "query": "*" + value + "*"}
            s = s.query("query_string", **filter_dict)

    return s.sort("-index_timestamp")[:limit].execute()
