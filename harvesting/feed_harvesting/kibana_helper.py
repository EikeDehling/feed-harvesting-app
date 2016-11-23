

def create_saved_search(es, saved_search_id, title, query):
    es.create(index='.kibana',
              doc_type="search",
              id=saved_search_id,
              body=dict(
                  title=title,
                  kibanaSavedObjectMeta= {
                      "searchSourceJSON": "{\"index\": \"rss-*\", \"query\": \"{0}\"}".format(query)
                  }
              ))

def create_volume_chart(es, volume_chart_id, saved_search_id, title):
    es.create(index='.kibana',
              doc_type="visualization",
              id=volume_chart_id,
              body=dict(
                  title=title,
                  visState="{\"title\":\"{0}\",\"type\":\"histogram\",\"params\":{\"shareYAxis\":true,\"addTooltip\":true,\"addLegend\":true,\"scale\":\"linear\",\"mode\":\"stacked\",\"times\":[],\"addTimeMarker\":false,\"defaultYExtents\":false,\"setYExtents\":false,\"yAxis\":{}},\"aggs\":[{\"id\":\"1\",\"type\":\"count\",\"schema\":\"metric\",\"params\":{}},{\"id\":\"2\",\"type\":\"date_histogram\",\"schema\":\"segment\",\"params\":{\"field\":\"published\",\"interval\":\"auto\",\"customInterval\":\"2h\",\"min_doc_count\":1,\"extended_bounds\":{}}}],\"listeners\":{}}".format(title),
                  uiStateJSON=dict(),
                  description="",
                  savedSearchId=saved_search_id,
                  version=1,
                  kibanaSavedObjectMeta=dict(
                      searchSourceJSON="{\"filter\":[]}"
                  )
              ))


def create_dashboard(es, dashboard_id, volume_chart_id, title):
    es.create(index='.kibana',
              doc_type="search",
              id=dashboard_id,
              body=dict(
                  title=title,
                  panelsJSON="[{\"id\":\"{0}\",\"type\":\"visualization\",\"panelIndex\":1,\"size_x\":10,\"size_y\":4,\"col\":1,\"row\":1}]".format(volume_chart_id),
                  optionsJSON="{\"darkTheme\":false}",
                  uiStateJSON="{\"P-1\":{\"vis\":{\"legendOpen\":false}}}",
                  timeRestore=True,
                  timeTo="now",
                  timeFrom="now-7d",
                  kibanaSavedObjectMeta=dict(
                      searchSourceJSON="{\"filter\":[{\"query\":{\"query_string\":{\"query\":\"*\",\"analyze_wildcard\":true}}}]}"
                  )
              ))
