from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet


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
        'size': 10,
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
                    'size': 15
                }
            },
            'top_sites': {
                'terms': {
                    'field': 'site',
                    'size': 8
                }
            },
            'languages': {
                'terms': {
                    'field': 'language',
                    'size': 4
                }
            },
            'publications': {
                'terms': {
                    'field': 'publication_name',
                    'size': 7
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

    cloud_data = [(bucket['key'], int((float(bucket['doc_count']) / float(bucket['bg_count'])) * 100.0))
                  for bucket in data['aggregations']['wordcloud']['buckets']]

    sites_data = [(bucket['key'], int(bucket['doc_count']))
                  for bucket in data['aggregations']['top_sites']['buckets']]

    langs = dict(
        en='English',
        de='German',
        fr='French',
        nl='Dutch',
        it='Italian',
        se='Spanish'
    )

    languages_data = [(langs.get(bucket['key'], bucket['key']), int(bucket['doc_count']))
                      for bucket in data['aggregations']['languages']['buckets']]

    publication_data = [(bucket['key'], int(bucket['doc_count']))
                        for bucket in data['aggregations']['publications']['buckets']]

    styles = getSampleStyleSheet()

    articles = [
        (art['_source']['published'].split('T')[0], art['_source']['publication_name'],
         Paragraph(art['_source']['title'], styles['Normal'])) for art in data['hits']['hits']
    ]

    return (data['hits']['total'], volume_chart_data, sentiment_data, cloud_data, sites_data,
            languages_data, publication_data, articles)