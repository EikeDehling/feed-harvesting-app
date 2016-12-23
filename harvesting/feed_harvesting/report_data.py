def generate_report_data(es):
    data = es.search(index='rss', doc_type='posting', body={
        'query': {
            'bool': {
                'must': [
                    {
                        'range': {
                            'published': {
                                'gte': '1/11/2016',
                                'lte': '30/11/2016',
                                'format': 'dd/MM/yyyy'
                            }
                        }
                    },
                    {
                        'match': {
                            '_all': 'trump'
                        }
                    }
                ]
            }
        },
        'size': 0,
        'aggs': {
            'timeline': {
                'date_histogram': {
                    'field': 'published',
                    'interval': 'day',
                    'format': 'yyyyMMdd'
                }
            },
            'sentiment': {
                'terms': {
                    'field': 'sentiment'
                }
            },
            'wordcloud': {
                'significant_terms': {
                    'field': 'description',
                    'size': 25
                }
            }
        }
    })

    volume_chart_data = [[(int(bucket['key_as_string']), int(bucket['doc_count']))
                          for bucket in data['aggregations']['timeline']['buckets']]]

    sentiments = {}
    for bucket in data['aggregations']['sentiment']['buckets']:
        sentiments[bucket['key']] = bucket['doc_count']

    sentiment_data = (float(sentiments['neutral']), float(sentiments['positive']), float(sentiments['negative']))

    cloud_data = [(bucket['key'], int(bucket['doc_count']))
                  for bucket in data['aggregations']['wordcloud']['buckets']]

    return (data['hits']['total'], volume_chart_data, sentiment_data, cloud_data)