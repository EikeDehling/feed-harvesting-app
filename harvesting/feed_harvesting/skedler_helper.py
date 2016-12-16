import time


def schedule_report(es, title, email, dashboard_id):
    # Schedule the report to me emailed at now + 10 minutes
    ts = time.localtime(time.time() + 60*10 + 3600)

    min = ts[4]
    hour = ts[3]
    day_of_week = ts[6]

    if min%10 < 2:
        min += 2
    if min%10 >= 8:
        min -= 2

    weekdays = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT', 'SUN']

    cron_line = '0 {min} {hour}  * * {day_of_week}'\
        .format(min=min, hour=hour, day_of_week=weekdays[day_of_week])

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
                              "cron": cron_line,
                              "Minutes": min,
                              "Hours": hour,
                              "weekdays": [weekdays[day_of_week]],
                              "type": "Weekly",
                              "timerange": "_g=(time:(from:now%2Fw,mode:quick,to:now%2Fw))"
                          }
                      ],
                      "useDashboardTime": True,
                      "emailDetails": {
                            "cc": "e.e.dehling@gmail.com",
                            "to": email,
                            "message": "Hi\nCheck out your report\nThanks",
                            "subject": title,
                            "format": "pdf"
                      },
                      "filter_name": "No Filter",
                      "folderpath": "",
                      "excelEnabled": False,
                      "OEM": {}
                  })

    return result['_id']
