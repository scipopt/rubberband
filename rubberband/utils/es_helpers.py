from datetime import datetime, timedelta


def get_uniques(model, field):
    '''
    Take an elasticsearch model and a field name. The looks up all of the possible values
    for that field in elasticsearch.
    '''
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
