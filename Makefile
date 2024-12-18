mig:
	python3 manage.py makemigrations
	python3 manage.py migrate

celery:
	celery -A root worker --loglevel=info

run:
	python3 manage.py runserver

superuser:
	python3 manage.py createsuperuser