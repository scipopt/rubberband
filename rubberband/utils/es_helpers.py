"""Helper methods for elasticsearch queries."""
from datetime import datetime, timedelta


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
    body = {'aggs': {'counts': {'terms': {'field': field, 'size': 0}}}}
    response = getattr(model, "search")().from_dict(body).execute()
    values = [i.key for i in response.aggregations.counts.buckets]

    today = datetime.now()
    threemonthsago = (today + timedelta(days=-100)).strftime('%Y-%m-%d')
    # TODO make this work for the most recent testruns
    body = {"filter": {"range": {"git_commit_timestamp": {"gte": threemonthsago}}},
            "aggs": {"hot_counts": {"terms": {"field": field, "size": 5}}}}

    response = getattr(model, "search")().from_dict(body).execute()
    hot_values = [i.key for i in response.aggregations.hot_counts.buckets]
    values = [v for v in values if v not in hot_values]
    return values, hot_values
