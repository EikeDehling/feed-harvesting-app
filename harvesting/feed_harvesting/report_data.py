

INDEX_PATTERN = 'rss-*'


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
                'size': 25,
                #'background_filter': {
                #    'query_string': {
                #        'query': 'trump'
                #    }
                #},
                "exclude" : {
                    "pattern": "[0-9]+"
                }
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

    volume_legend_data = [ '%s\n(%d hits)' % (report.query, data['hits']['total']) ]
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

    articles = [
        (art['_source']['published'].split('T')[0], art['_source']['publication_name'], art['_source']['title'])
        for art in data['hits']['hits']
    ]

    return {
        'volume_chart_data': volume_chart_data,
        'volume_legend_data': volume_legend_data,
        'sentiment_data': sentiment_data,
        'wordcloud_data': cloud_data,
        'sites_data': sites_data,
        'languages_data': languages_data,
        'publication_data': publication_data,
        'reputation_data': rep_data,
        'media_type_data': media_type_data,
        'articles': articles
    }


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

    articles = [
        (art['_source']['published'].split('T')[0], art['_source']['publication_name'], art['_source']['title'])
        for art in all_data['aggregations']['benchmark']['hits']['hits']['hits']
    ]

    return {
        'volume_chart_data': volume_chart_data,
        'volume_legend_data': volume_legend_data,
        'sentiment_data': sentiment_data,
        'sentiment_bench_data': sentiment_bench_data,
        'wordcloud_data': cloud_data,
        'sites_data': sites_data,
        'languages_data': languages_data,
        'publication_data': publication_data,
        'reputation_data': rep_data,
        'media_type_data': media_type_data,
        'articles': articles
    }


def generate_extended_report_data(es, report):
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
        'aggs': {
            'timeline': {
                'date_histogram': {
                    'field': 'published',
                    'interval': 'day',
                    'format': 'yyyyMMdd'
                }
            }
        }
    }

    data = es.search(index=INDEX_PATTERN, doc_type='posting', body=body)

    body = {
        'query': {
            'bool': {
                'must': [
                    {
                        'range': {
                            'published': {
                                'gte': 'now-30d/d',
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
        'aggs': {
            'timeline': {
                'date_histogram': {
                    'field': 'published',
                    'interval': 'day',
                    'format': 'yyyyMMdd'
                }
            },
            'volume_stats': {
                'extended_stats_bucket': {
                    'buckets_path': 'timeline._count',
                    'sigma': 1.5
                }
            }
        }
    }

    data_month = es.search(index=INDEX_PATTERN, doc_type='posting', body=body)

    volume_legend_data = [ '%s\n(%d hits)' % (report.query, data['hits']['total']) ]
    volume_chart_data = [[(int(bucket['key_as_string']), int(bucket['doc_count']))
                          for bucket in data['aggregations']['timeline']['buckets']]]

    volume_stats_data = data_month['aggregations']['volume_stats']


    return {
        'volume_chart_data': volume_chart_data,
        'volume_legend_data': volume_legend_data,
        'volume_stats_data': volume_stats_data
    }