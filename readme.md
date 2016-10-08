[Installing]

virtualenv .
bin/pip install django
bin/pip install elasticsearch
bin/pip install feedparser

[Running admin UI]

bin/python manage.py runserver

[Runnig feed harvester]

bin/python manage.py fetch

