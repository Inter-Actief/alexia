setup-local:
	pip install -r requirements.txt
	cp alexia/conf/settings/local.py.default alexia/conf/settings/local.py
	python manage.py migrate
	python manage.py runserver

setup-docker:
	cp alexia/conf/settings/local.py.default alexia/conf/settings/local.py
	docker compose up -d --build
	docker compose exec app python manage.py migrate
