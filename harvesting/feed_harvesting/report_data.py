from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet

from .models import ComparisonReport


INDEX_PATTERN = 'rss-*'


def generate_report_data(es, report):
    body = {
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
                    }
                ]
            }
        },
        'size': 0,
        'aggs': {
            'main': {
                'filter': {
                    'match': {
                        '_all': report.query
                    }
                },
                'aggs': {
                    'hits': {
                      'top_hits': {
                          'size': 10
                      }
                    },
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
            }
        }
    }

    def extend_comparo(name, query):
        body['aggs'][name] = {
            'filter': {
                'match': {
                    '_all': query
                }
            },
            'aggs': {
                'hits': {
                    'top_hits': {
                        'size': 10
                    }
                },
                'timeline': {
                    'date_histogram': {
                        'field': 'published',
                        'interval': 'day',
                        'format': 'yyyyMMdd'
                    }
                }
            }
        }

    volume_legend_dict = {
        'main': report.query
    }

    if isinstance(report, ComparisonReport):
        if report.compare_one:
            volume_legend_dict['one'] = report.compare_one
            extend_comparo('one', report.compare_one)
        if report.compare_two:
            volume_legend_dict['two'] = report.compare_two
            extend_comparo('two', report.compare_two)
        if report.compare_three:
            volume_legend_dict['three'] = report.compare_three
            extend_comparo('three', report.compare_three)

    data = es.search(index=INDEX_PATTERN, doc_type='posting', body=body)

    volume_chart_data = []
    volume_legend_data = []

    for name in data['aggregations']:
        agg = data['aggregations'][name]
        volume_legend_data.append('%s\n(%d hits)' % (volume_legend_dict[name],
                                                     agg['hits']['hits']['total']))
        volume_chart_data.append([(int(bucket['key_as_string']), int(bucket['doc_count']))
                                  for bucket in agg['timeline']['buckets']])

    # Hack TODO
    data = data['aggregations']['main']

    sentiments = {}
    for bucket in data['sentiment']['buckets']:
        sentiments[bucket['key']] = bucket['doc_count']

    sentiment_data = (float(sentiments.get('neutral', 0)),
                      float(sentiments.get('positive', 0)),
                      float(sentiments.get('negative', 0)))

    cloud_data = [(bucket['key'], int((float(bucket['doc_count']) / float(bucket['bg_count'])) * 100.0))
                  for bucket in data['wordcloud']['buckets']]

    sites_data = [(bucket['key'], int(bucket['doc_count']))
                  for bucket in data['top_sites']['buckets']]

    langs = dict(
        en='English',
        de='German',
        fr='French',
        nl='Dutch',
        it='Italian',
        se='Spanish'
    )

    languages_data = [(langs.get(bucket['key'], bucket['key']), int(bucket['doc_count']))
                      for bucket in data['languages']['buckets']]

    publication_data = [(bucket['key'], int(bucket['doc_count']))
                        for bucket in data['publications']['buckets']]

    styles = getSampleStyleSheet()

    articles = [
        (art['_source']['published'].split('T')[0], art['_source']['publication_name'],
         Paragraph(art['_source']['title'], styles['Normal'])) for art in data['hits']['hits']['hits']
    ]

    return (volume_chart_data, volume_legend_data, sentiment_data, cloud_data, sites_data,
            languages_data, publication_data, articles)