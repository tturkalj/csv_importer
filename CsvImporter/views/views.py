from flask import Blueprint, render_template, abort, request
from jinja2 import TemplateNotFound
from CsvImporter.models.database import Session
from CsvImporter.models.models import Device, DeviceContent, ImporterSettings

main_view = Blueprint('main_view', __name__)


@main_view.route('/')
def index():
    devices = Session.query(Device).all()
    context = {'devices': devices}
    return render_template('index.jinja2', **context)


@main_view.route('/device/content')
def device_content():
    device_content_query = Session.query(DeviceContent).all()
    context = {'device_content': device_content_query}
    return render_template('device_content.jinja2', **context)


@main_view.route('/settings', methods=['GET', 'POST'])
def settings():
    settings_query = Session.query(ImporterSettings).first()
    if request.method == 'POST':
        settings_query.csv_store_pat = request.form['csv_store_path']
        settings_query.device_file_name = request.form['device_file_name']
        settings_query.content_file_name = request.form['content_file_name']
        settings_query.default_csv_delimiter = request.form['default_csv_delimiter']
        Session.flush()

    context = {'settings': settings_query}

    return render_template('settings.jinja2', **context)
