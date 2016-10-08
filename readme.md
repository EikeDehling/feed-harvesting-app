[Installing]

virtualenv .
bin/pip install django
bin/pip install elasticsearch
bin/pip install feedparser

[Running admin UI]

cd harvesting
../bin/python manage.py runserver 0.0.0.0:8000 --insecure

[Runnig feed harvester]

bin/python manage.py fetch

