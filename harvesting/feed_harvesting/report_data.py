INDEX_PATTERN = 'rss-*'

def generate_report_data(es, keywords):
    data = es.search(index=INDEX_PATTERN, doc_type='posting', body={
        'query': {
            'bool': {
                'must': [
                    {
                        'range': {
                            'published': {
                                'gte': 'now-14d/d',
                                'lte': 'now/d'
                            }
                        }
                    },
                    {
                        'match': {
                            '_all': keywords
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
                    'size': 20
                }
            },
            'top_sites': {
                'terms': {
                    'field': 'site',
                    'size': 8
                }
            }
        }
    })

    volume_chart_data = [[(int(bucket['key_as_string']), int(bucket['doc_count']))
                          for bucket in data['aggregations']['timeline']['buckets']]]

    sentiments = {}
    for bucket in data['aggregations']['sentiment']['buckets']:
        sentiments[bucket['key']] = bucket['doc_count']

    sentiment_data = (float(sentiments.get('neutral', 0)),
                      float(sentiments.get('positive', 0)),
                      float(sentiments.get('negative', 0)))

    cloud_data = [(bucket['key'], int(bucket['doc_count']))
                  for bucket in data['aggregations']['wordcloud']['buckets']]

    sites_data = [(bucket['key'], int(bucket['doc_count']))
                  for bucket in data['aggregations']['top_sites']['buckets']]

    return (data['hits']['total'], volume_chart_data, sentiment_data, cloud_data, sites_data)