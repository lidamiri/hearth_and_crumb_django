PYTHON ?= python3
VENV ?= .venv
BIN := $(VENV)/bin
NAME := hearth-and-crumb-django
DIST := dist

.PHONY: help venv install migrate seed run test check shell superuser static zip clean

help:
	@echo "Targets: install migrate seed run test check shell superuser static zip clean"

venv:
	$(PYTHON) -m venv $(VENV)

install: venv
	$(BIN)/pip install --upgrade pip
	$(BIN)/pip install -r requirements.txt

migrate:
	$(BIN)/python manage.py migrate

seed:
	$(BIN)/python manage.py seed_catalog

run:
	$(BIN)/python manage.py runserver 0.0.0.0:8000

test:
	$(BIN)/python manage.py test --verbosity 2

check:
	$(BIN)/python manage.py check

shell:
	$(BIN)/python manage.py shell

superuser:
	$(BIN)/python manage.py createsuperuser

static:
	$(BIN)/python manage.py collectstatic --noinput

zip:
	mkdir -p $(DIST)
	git archive --format=zip --prefix=$(NAME)/ -o $(DIST)/$(NAME).zip HEAD

clean:
	rm -rf $(DIST) staticfiles
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
