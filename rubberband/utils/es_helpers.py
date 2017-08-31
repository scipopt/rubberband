from datetime import datetime, timedelta

def get_uniques(model, field):
    '''
    Take an elasticsearch model and a field name. The looks up all of the possible values
    for that field in elasticsearch.
    '''
    body = {'aggs': {'counts': {'terms': {'field': field, 'size': 0}}}}
    # this should be the same as 'model.search()'.from_dict(body).execute() ...
    response = getattr(model, "search")().from_dict(body).execute()
    values = [i.key for i in response.aggregations.counts.buckets]

    #today = datetime.now()
    #threemonthsago = (today + timedelta(days=-100)).strftime('%Y-%m-%d')
    #body = {'filter': {'range': {'git_commit_timestamp': {'gte': threemonthsago }}} }#,
            #'aggs': {'hot_counts': {'terms': {'field': field, 'size': 5 }}}}
    # this should be the same as 'model.search()'.from_dict(body).execute() ...
    #response = getattr(model, "search")().from_dict(body).execute()
    #print("vorher")
    #print(response)
    #print("nachher")
    #hot_values = [i.key for i in response.aggregations.hot_counts.buckets]
    return values#, hot_values
