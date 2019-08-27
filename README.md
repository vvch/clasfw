# CLAS Analysis Framework

## Installation

Pre-requisites:

  * python 3.7+
  * stylus (install `node.js`, `npm` and run `npm install stylus`)
  * wsgi-capable web-server, e. g. `gunicorn`
  * install dependencies by running `pip install -r requirements.txt` in application's root folder.


## Tests

Run the following command in application's root folder:

    py.test

## Setup

Run following commands in project's root folder:

    flask assets build
    flask db upgrade
    flask gen all

to create data storage and fill it with test data sets.


## Running

Start web-server passing application instance to it, e. g.:

    gunicorn clasfw.app:create_app
