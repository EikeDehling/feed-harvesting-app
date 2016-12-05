
def schedule_report(es, title, dashboard_id):
    result = es.index(index='.skedler',
                  doc_type="jobs",
                  body={
                      "title": title,
                      "kibana_object_type": "dashboard",
                      "kibana_object_id": dashboard_id,
                      "layout": {
                          "reportFont": "Default Font",
                          "reportLogoPath": "logo/logo.png",
                          "reportLogo": "defaultLogo",
                          "smartLayout": False,
                          "layoutType": "Default Size",
                          "reportTitle": title,
                          "orientation": "portrait"
                      },
                      "shieldPlugin": {},
                      "timeWindow": {
                          "type": "quick",
                          "timeFrom": {
                              "type": "",
                              "val": "now-1w"
                          },
                          "timeTo": {
                              "type": "",
                              "val": "now"
                          },
                          "roundOff": False
                      },
                      "jobStatus": "resume",
                      "includefilter": False,
                      "cron": [
                          {
                              "Hours": 9,
                              "type": "Weekly",
                              "timerange": "_g=(time:(from:now%2Fw,mode:quick,to:now%2Fw))",
                              "weekdays": [
                                  "MON"
                              ],
                              "cron": "0 0 9  * * MON",
                              "Minutes": 0
                          }
                      ],
                      "useDashboardTime": True,
                      "emailDetails": {
                            "cc": "e.e.dehling@gmail.com",
                            "to": "daan@mediamatters.asia",
                            "message": "Hi\nCheck out the report\nThanks",
                            "subject": title,
                            "format": "pdf"
                      },
                      "filter_name": "No Filter",
                      "folderpath": "",
                      "excelEnabled": False,
                      "OEM": {}
                  })

    return result['_id']