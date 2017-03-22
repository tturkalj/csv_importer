# -*- coding: utf-8 -*-
import logging
from flask import Flask
from CsvImporter.views.views import main_view


def create_app(config=None):
    flask_app = Flask(__name__, static_url_path='/static')
    return flask_app


if __name__ == '__main__':
    app = create_app()
    app.register_blueprint(main_view)
    app.run()




