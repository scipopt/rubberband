"""Helper methods for elasticsearch queries."""
from datetime import datetime, timedelta

from rubberband.constants import MAX_VALUE_RECORDS
from elasticsearch import TransportError


def get_uniques(model, field):
    """
    Look up all of the possible values for a field in elasticsearch.

    Parameters
    ----------
    model : rubberband.model
        Model to get values from.
    field : attribute
        Field of model to get values from.

    Returns
    -------
        all possible values and the 5 most common ones.
    """
    body = {'aggs': {'counts': {'terms': {'field': field, 'size': MAX_VALUE_RECORDS}}}}
    response = getattr(model, "search")().from_dict(body).execute()
    values = [i.key for i in response.aggregations.counts.buckets]

    today = datetime.now()
    threemonthsago = (today + timedelta(days=-100)).strftime('%Y-%m-%d')
    # TODO make this work for the most recent testruns
    body = {"query": {"range": {"git_commit_timestamp": {"gte": threemonthsago}}},
            "aggs": {"hot_counts": {"terms": {"field": field, "size": 5}}}}

    try:
        response = getattr(model, "search")().from_dict(body).execute()
    except TransportError as e:
        print(e.info)

    hot_values = [i.key for i in response.aggregations.hot_counts.buckets]
    values = [v for v in values if v not in hot_values]
    return values, hot_values
