import json


INDEX_PATTERN = 'rss-*'


def create_saved_search(es, title, query):
    result = es.index(index='.kibana',
                      doc_type="search",
                      body=dict(
                          title=title,
                          kibanaSavedObjectMeta={
                              "searchSourceJSON": '{"index": "%s", "query": "%s"}' % (INDEX_PATTERN, query)
                          }
                      ))
    return result['_id']


def create_volume_chart(es, saved_search_id, title):
    result = es.index(index='.kibana',
                      doc_type="visualization",
                      body=dict(
                          title=title,
                          visState='{"title":"%s","type":"histogram","params":{"shareYAxis":true,"addTooltip":true,"addLegend":true,"scale":"linear","mode":"stacked","times":[],"addTimeMarker":false,"defaultYExtents":false,"setYExtents":false,"yAxis":{}},"aggs":[{"id":"1","type":"count","schema":"metric","params":{}},{"id":"2","type":"date_histogram","schema":"segment","params":{"field":"published","interval":"auto","customInterval":"2h","min_doc_count":1,"extended_bounds":{}}}],"listeners":{}}' % title,
                          uiStateJSON="{}",
                          description="",
                          savedSearchId=saved_search_id,
                          version=1,
                          kibanaSavedObjectMeta=dict(
                              searchSourceJSON='{"filter":[]}'
                          )
                      ))
    return result['_id']


def create_sentiment_chart(es, saved_search_id, title):
    result = es.index(index='.kibana',
                      doc_type="visualization",
                      body=dict(
                          title=title,
                          visState='{"title":"%s","type":"pie","params":{"shareYAxis":true,"addTooltip":true,"addLegend":true,"isDonut":false},"aggs":[{"id":"1","type":"count","schema":"metric","params":{}},{"id":"2","type":"terms","schema":"segment","params":{"field":"sentiment","size":5,"order":"desc","orderBy":"1"}}],"listeners":{}}' % title,
                          uiStateJSON='{"vis":{"colors":{"neutral":"#999999","positive":"#00FF00","negative":"#FF0000"}}}',
                          description="",
                          savedSearchId=saved_search_id,
                          version=1,
                          kibanaSavedObjectMeta=dict(
                              searchSourceJSON='{"filter":[]}'
                          )
                      ))
    return result['_id']


def create_top_sites_chart(es, saved_search_id, title):
    result = es.index(index='.kibana',
                      doc_type="visualization",
                      body={
                          "title": title,
                          "visState": '{"title":"%s","type":"table","params":{"perPage":15,"showPartialRows":false,"showMeticsAtAllLevels":true},"aggs":[{"id":"1","type":"count","schema":"metric","params":{}},{"id":"2","type":"terms","schema":"bucket","params":{"field":"site","size":24,"order":"desc","orderBy":"1"}}],"listeners":{}}' % title,
                          "uiStateJSON": "{}",
                          "savedSearchId": saved_search_id,
                          "kibanaSavedObjectMeta": {
                              "searchSourceJSON": '{"filter":[],"highlight":{"pre_tags":["@kibana-highlighted-field@"],"post_tags":["@/kibana-highlighted-field@"],"fields":{"*":{}},"require_field_match":false,"fragment_size":2147483647}}}'
                          }
                      })
    return result['_id']


def create_tagcloud_chart(es, saved_search_id, title):
    result = es.index(index='.kibana',
                      doc_type="visualization",
                      body=dict(
                          title=title,
                          visState='{"title":"%s","type":"tagcloud","params":{"textScale":"linear","orientations":1,"fromDegree":0,"toDegree":0,"font":"serif","fontStyle":"normal","fontWeight":"normal","timeInterval":500,"spiral":"archimedean","minFontSize":18,"maxFontSize":72},"aggs":[{"id":"1","type":"count","schema":"metric","params":{}},{"id":"2","type":"significant_terms","schema":"segment","params":{"field":"title","size":50}}],"listeners":{}}' % title,
                          uiStateJSON='{"spy":{"mode":{"name":null,"fill":false}}}',
                          description='',
                          savedSearchId=saved_search_id,
                          kibanaSavedObjectMeta=dict(
                              searchSourceJSON='{"filter":[]}'
                          )
                      ))
    return result['_id']


def create_languages_chart(es, saved_search_id, title):
    result = es.index(index='.kibana',
                      doc_type="visualization",
                      body=dict(
                          title=title,
                          visState='{"title":"%s","type":"pie","params":{"shareYAxis":true,"addTooltip":true,"addLegend":true,"isDonut":false},"aggs":[{"id":"1","type":"count","schema":"metric","params":{}},{"id":"2","type":"terms","schema":"segment","params":{"field":"language","size":5,"order":"desc","orderBy":"1"}}],"listeners":{}}' % title,
                          uiStateJSON='{}',
                          description="",
                          savedSearchId=saved_search_id,
                          version=1,
                          kibanaSavedObjectMeta=dict(
                              searchSourceJSON='{"filter":[]}'
                          )
                      ))
    return result['_id']


def create_dashboard(es, volume_chart_id, sentiment_chart_id, sites_chart_id, tagcloud_chart_id,
                     languages_chart_id, title):
    panels_json = [
        {
            "id": volume_chart_id,
            "type": "visualization",
            "panelIndex": 1,
            "size_x": 10,
            "size_y": 4,
            "col": 1,
            "row": 1
        },
        {
            "id": sentiment_chart_id,
            "type": "visualization",
            "panelIndex": 2,
            "size_x": 5,
            "size_y": 4,
            "col": 1,
            "row": 5
        },
        {
            "id": sites_chart_id,
            "type": "visualization",
            "panelIndex": 3,
            "size_x": 5,
            "size_y": 4,
            "col": 6,
            "row": 5
        },
        {
            "id": languages_chart_id,
            "type": "visualization",
            "panelIndex": 4,
            "size_x": 5,
            "size_y": 4,
            "col": 1,
            "row": 9
        },
        #{
        #    "id": tagcloud_chart_id,
        #    "type": "visualization",
        #    "panelIndex": 5,
        #    "size_x": 5,
        #    "size_y": 4,
        #    "col": 6,
        #    "row": 9
        #}
    ]

    result = es.index(index='.kibana',
                      doc_type="dashboard",
                      body=dict(
                          title=title,
                          panelsJSON=json.dumps(panels_json),
                          optionsJSON='{"darkTheme":false}',
                          uiStateJSON='{"P-1":{"vis":{"legendOpen":false}}}',
                          timeRestore=True,
                          timeTo="now",
                          timeFrom="now-7d",
                          kibanaSavedObjectMeta={
                              'searchSourceJSON': '{"filter":[{"query":{"query_string":{"query":"*","analyze_wildcard":true}}}]}'
                          }
                      ))
    return result['_id']
