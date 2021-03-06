from reportlab.platypus import Paragraph
from reportlab.lib.styles import getSampleStyleSheet


INDEX_PATTERN = 'rss-2017-01'


language_codes_to_name = dict(
    en='English',
    de='German',
    fr='French',
    nl='Dutch',
    it='Italian',
    se='Spanish',
    id='Indonesian'
)


def _aggregations():
    return {
        'timeline': {
            'date_histogram': {
                'field': 'published',
                'interval': 'day',
                'format': 'yyyyMMdd'
            }
        },
        'sentiment': {
            'terms': {
                'field': 'sentiment',
                'size': 3
            }
        },
        'wordcloud': {
            'significant_terms': {
                'field': 'description',
                'size': 25
            }
        },
        'top_sites': {
            'terms': {
                'field': 'site',
                'size': 5
            }
        },
        'languages': {
            'terms': {
                'field': 'language',
                'size': 3
            }
        },
        'media_types': {
            'terms': {
                'field': 'media_type',
                'size': 0
            }
        },
        'publications': {
            'terms': {
                'field': 'publication_name',
                'size': 5
            }
        },
        'reputation_drivers': {
            'filters': {
                'filters': {
                    'Products/\nServices': {"match": {"_all": "quality product service"}},
                    'Innovation': {"match": {"_all": "innovate innovation modern hightech hitech creative technology"}},
                    'Workplace': {"match": {"_all": "salary workplace employer employee motivating"}},
                    'Governance': {"match": {"_all": "governance regulatory institutionalized corporate participatory"}},
                    'Citizenship': {"match": {"_all": "ngo donation donate human rights mvo responsible environment green ecological"}},
                    'Leadership': {"match": {"_all": "ceo cfo board leader leadership executive chief"}},
                    'Performance': {"match": {"_all": "performance revenue income turnover quarter growth"}}
                }
            }
        }
    }


def generate_report_data(es, report):
    body = {
        'query': {
            'bool': {
                'must': [
                    {
                        'range': {
                            'published': {
                                'gte': 'now-7d/d',
                                'lte': 'now'
                            }
                        }
                    },
                    {
                        'query_string': {
                            'query': report.query
                        }
                    }
                ]
            }
        },
        'size': 10,
        'aggs': _aggregations()
    }

    data = es.search(index=INDEX_PATTERN, doc_type='posting', body=body)

    body = {
        "search_request": {
            "query": {
                "and": [
                    {
                        "match": {
                            "_all": "donald trump"
                        }
                    },
                    {
                        'range': {
                            'published': {
                                'gte': 'now-2d/d',
                                'lte': 'now'
                            }
                        }
                    }
                ]
            },
            "size": 10000
        },
        "query_hint": "donald trump",
        "field_mapping": {
            "title": [ "_source.title" ],
            "content": [ "_source.description" ]
        },
        "algorithm": "lingo",
        "include_hits": False,
        "attributes": {
            "LingoClusteringAlgorithm.desiredClusterCountBase": 20,
            "LingoClusteringAlgorithm.clusterMergingThreshold": 0.4,
        }
    }

    tagcloud_data = es.transport.perform_request('POST', '/rss-2017-01/_search_with_clusters',
                                                 params={'request_timeout': 30}, body=body)

    volume_legend_data = [ '%s\n(%d hits)' % (report.query, data['hits']['total']) ]
    volume_chart_data = [[(int(bucket['key_as_string']), int(bucket['doc_count']))
                           for bucket in data['aggregations']['timeline']['buckets']]]

    sentiments = {}
    for bucket in data['aggregations']['sentiment']['buckets']:
        sentiments[bucket['key']] = bucket['doc_count']

    sentiment_data = (float(sentiments.get('neutral', 0)),
                      float(sentiments.get('positive', 0)),
                      float(sentiments.get('negative', 0)))

    #cloud_data = [(bucket['key'], int((float(bucket['doc_count']) / float(bucket['bg_count'])) * 100.0))
    #              for bucket in data['aggregations']['wordcloud']['buckets']]

    cloud_data = [(cluster['label'], int(len(cluster['documents']))) for cluster in tagcloud_data['clusters']]

    sites_data = [[(bucket['key'], int(bucket['doc_count']))
                   for bucket in data['aggregations']['top_sites']['buckets']]]

    languages_data = [(language_codes_to_name.get(bucket['key'], bucket['key']), int(bucket['doc_count']))
                      for bucket in data['aggregations']['languages']['buckets']]

    publication_data = [[(bucket['key'], int(bucket['doc_count']))
                         for bucket in data['aggregations']['publications']['buckets']]]

    media_type_data = [(bucket['key'], int(bucket['doc_count']))
                       for bucket in data['aggregations']['media_types']['buckets']]

    rep_data = [[(bucket_name, int(data['aggregations']['reputation_drivers']['buckets'][bucket_name]['doc_count']))
                 for bucket_name in data['aggregations']['reputation_drivers']['buckets']]]

    styles = getSampleStyleSheet()

    articles = [
        (art['_source']['published'].split('T')[0], art['_source']['publication_name'],
         Paragraph(art['_source']['title'], styles['Normal'])) for art in data['hits']['hits']
    ]

    return (volume_chart_data, volume_legend_data, sentiment_data, None, cloud_data, sites_data,
            languages_data, publication_data, rep_data, media_type_data, articles)


def generate_copmarison_report_data(es, report):
    body = {
        'query': {
            'bool': {
                'must': [
                    {
                        'range': {
                            'published': {
                                'gte': 'now-7d/d',
                                'lte': 'now'
                            }
                        }
                    }
                ]
            }
        },
        'size': 0,
        'aggs': {}
    }

    def extend_comparo(name, query):
        body['aggs'][name] = {
            'filter': {
                'query_string': {
                    'query': query
                }
            },
            'aggs': dict(
                hits = dict(top_hits=dict(size=10)),
                **_aggregations()
            )
        }

    volume_legend_dict = {}

    volume_legend_dict['main'] = report.query
    extend_comparo('main', report.query)

    if report.compare_one:
        volume_legend_dict['one'] = report.compare_one
        extend_comparo('one', report.compare_one)
    if report.compare_two:
        volume_legend_dict['two'] = report.compare_two
        extend_comparo('two', report.compare_two)
    if report.compare_three:
        volume_legend_dict['three'] = report.compare_three
        extend_comparo('three', report.compare_three)

    benchmark_query = ' '.join(volume_legend_dict.values())
    volume_legend_dict['benchmark'] = benchmark_query
    extend_comparo('benchmark', benchmark_query)

    all_data = es.search(index=INDEX_PATTERN, doc_type='posting', body=body)

    volume_chart_data = []
    volume_legend_data = []

    for name in all_data['aggregations']:
        if name == 'benchmark':
            continue
        agg = all_data['aggregations'][name]
        volume_legend_data.append('%s\n(%d hits)' % (volume_legend_dict[name],
                                                     agg['hits']['hits']['total']))
        volume_chart_data.append([(int(bucket['key_as_string']), int(bucket['doc_count']))
                                  for bucket in agg['timeline']['buckets']])

    sentiments = {}
    for bucket in all_data['aggregations']['main']['sentiment']['buckets']:
        sentiments[bucket['key']] = bucket['doc_count']

    sentiment_data = (float(sentiments.get('neutral', 0)),
                      float(sentiments.get('positive', 0)),
                      float(sentiments.get('negative', 0)))

    sentiments_bench = {}
    for bucket in all_data['aggregations']['benchmark']['sentiment']['buckets']:
        sentiments_bench[bucket['key']] = bucket['doc_count']

    sentiment_bench_data = (float(sentiments_bench.get('neutral', 0)),
                            float(sentiments_bench.get('positive', 0)),
                            float(sentiments_bench.get('negative', 0)))

    cloud_data = [(bucket['key'], int((float(bucket['doc_count']) / float(bucket['bg_count'])) * 100.0))
                  for bucket in all_data['aggregations']['benchmark']['wordcloud']['buckets']]

    sites_data = [[(bucket['key'], int(bucket['doc_count']))
                   for bucket in all_data['aggregations']['main']['top_sites']['buckets']]]

    languages_data = [
        [(language_codes_to_name.get(bucket['key'], bucket['key']), int(bucket['doc_count']))
         for bucket in all_data['aggregations']['main']['languages']['buckets']],
        [(language_codes_to_name.get(bucket['key'], bucket['key']), int(bucket['doc_count']))
         for bucket in all_data['aggregations']['benchmark']['languages']['buckets']],
    ]

    publication_data = [[(bucket['key'], int(bucket['doc_count']))
                         for bucket in all_data['aggregations']['main']['publications']['buckets']]]

    media_type_data = [(bucket['key'], int(bucket['doc_count']))
                       for bucket in all_data['aggregations']['main']['media_types']['buckets']]

    rep_data = [
        [(bucket_name, int(all_data['aggregations']['main']['reputation_drivers']['buckets'][bucket_name]['doc_count']))
         for bucket_name in all_data['aggregations']['main']['reputation_drivers']['buckets']],
        [(bucket_name, int(all_data['aggregations']['benchmark']['reputation_drivers']['buckets'][bucket_name]['doc_count']))
         for bucket_name in all_data['aggregations']['benchmark']['reputation_drivers']['buckets']]
    ]

    styles = getSampleStyleSheet()

    articles = [
        (art['_source']['published'].split('T')[0], art['_source']['publication_name'],
         Paragraph(art['_source']['title'], styles['Normal'])) for art in all_data['aggregations']['benchmark']['hits']['hits']['hits']
    ]

    return (volume_chart_data, volume_legend_data, sentiment_data, sentiment_bench_data, cloud_data, sites_data,
            languages_data, publication_data, rep_data, media_type_data, articles)