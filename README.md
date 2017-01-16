# [Alexia](https://alex.ia.utwente.nl)

[![Build Status](https://travis-ci.org/Inter-Actief/alexia.svg?branch=master)](https://travis-ci.org/Inter-Actief/alexia)
[![Requirements Status](https://requires.io/github/Inter-Actief/alexia/requirements.svg?branch=master)](https://requires.io/github/Inter-Actief/alexia/requirements/?branch=master)

Alexia is the management system for the drink rooms in the Zilverling at the University of Twente, the Abscint and MBasement.

## Table of contents

- [Quick start](#quick-start)
- [Project structure](#project-structure)

## Quick start

To set up your own copy of Alexia, use the following steps:

- Make sure you have a [virtualenv](https://virtualenv.pypa.io) set up.
- Clone the repo: `git clone https://github.com/Inter-Actief/alexia.git`
- Install the required packages: `pip install -r config/requirements.txt`
- Copy the default settings and edit to your likings.
  - `cp alexia/conf/settings/local.py.default alexia/conf/settings/local.py`
  - `vi alexia/conf/settings.py`
- Run the migrations: `python manage.py migrate`
- (optional) Create a super user: `python manage.py createsuperuser`
- Run it: `python manage.py runserver`

## Project structure

- alexia/ - All Python code
  - api/ - API logic
  - apps/ - Alexia logic
  - conf/wsgi.py - WSGI Application entry
  - conf/setttings/local.py.default - Example settings file
- assets/ - CSS/Webfonts/Images/Javascript
- bin/ - Auxilary scripts
- config/ - Configuration for the Alexia environment
- locale/ - Internationalization
- templates/ - Templates
