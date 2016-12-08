

def get_uniques(model, field):
    '''
    Take an elasticsearch model and a field name. The looks up all of the possible values
    for that field in elasticsearch.
    '''
    body = {'aggs': {'counts': {'terms': {'field': field}}}, 'size': 0}
    response = getattr(model, "search")().from_dict(body).execute()
    values = [i.key for i in response.aggregations.counts.buckets]
    return values
