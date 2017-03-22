# -*- coding: utf8 -*
import csv
import os
import logging
import transaction
from dateutil import parser
from logging.handlers import TimedRotatingFileHandler
from CsvImporter.models.database import Session
from CsvImporter.models.models import ImporterSettings, Device, DeviceContent
from CsvImporter import get_root_folder
from CsvImporter.utility.helper import StatusConstants, now

csv_import_errors_handler = TimedRotatingFileHandler(os.path.join(get_root_folder(), 'csv_import_errors/errors.log'),
                                                     when='midnight',
                                                     backupCount=365)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s - %(message)s')
csv_import_errors_handler.setLevel(logging.DEBUG)
csv_import_errors_handler.setFormatter(formatter)
csv_error_logger = logging.getLogger('csv_error_logger')
csv_error_logger.addHandler(csv_import_errors_handler)

log_handler = TimedRotatingFileHandler(os.path.join(get_root_folder(), 'log/app.log'),
                                       when='midnight',
                                       backupCount=365)
log_handler.setFormatter(formatter)
log_handler.setLevel(logging.DEBUG)
log = logging.getLogger(__name__)
log.addHandler(log_handler)


class CsvImporter(object):
    def __init__(self, csv_store_path=None, device_file_name=None, content_file_name=None, default_csv_delimiter=None):
        self.csv_store_path = csv_store_path
        self.device_file_name = device_file_name
        self.content_file_name = content_file_name
        self.default_csv_delimiter = default_csv_delimiter

    def set_settings(self):
        settings = Session.query(ImporterSettings).first()
        self.csv_store_path = settings.csv_store_path
        self.device_file_name = settings.device_file_name
        self.content_file_name = settings.content_file_name
        self.default_csv_delimiter = settings.default_csv_delimiter

    def utf_8_encoder(self, unicode_csv_data):
        for line in unicode_csv_data:
            yield line.encode('utf-8')

    def unicode_csv_reader(self, unicode_csv_data, delimiter, **kwargs):
        # csv.py doesn't do Unicode; encode temporarily as UTF-8:
        try:
            csv_reader = csv.reader(self.utf_8_encoder(unicode_csv_data), delimiter=str(delimiter), **kwargs)
            for row in csv_reader:
                # decode UTF-8 back to Unicode, cell by cell:
                yield [unicode(cell.strip(), 'utf-8') for cell in row]
        except Exception as e:
            log.exception(u'Error when reading CSV {0}'.format(e))

    def read_csv_file(self, file_name):
        """
        Method used for reading rows of CSV file.
        :param file_name: string
        :return: list of rows(lists) or None for error
        """
        file_path = os.path.abspath(os.path.join(get_root_folder(), self.csv_store_path, file_name))
        try:
            with open(file_path) as f:
                return [row for row in self.unicode_csv_reader(f, self.default_csv_delimiter)]
        except Exception as e:
            log.exception(u'Error when reading CSV file {0}: {1}'.format(file_name, e))
            return None

    def get_parsed_device_row(self, row, row_number):
        """
        Method used for getting dict of Device data from CSV row.
        :param row: CSV Device data row, list
        :param row_number: integer
        :return: dict {
            'id': integer, required,
            'name': string or None for invalid data,
            'description': string or None for invalid data,
            'code': string or None for invalid data,
            'expire_date': datetime or None for invalid data,
            'status': integer or None for invalid data
        } or None for error
        """

        if len(row) < 6:
            csv_error_logger.error(u'Device row {0} has invalid number of columns'.format(row_number))
            return None

        try:
            device_id = str(row[0])
            if not device_id.isdigit():
                csv_error_logger.error(u'Device in row {0} has invalid ID: {1}'.format(row_number, row[0]))
                return None
        except Exception as e:
            csv_error_logger.error(u'Device in row {0} has invalid ID: {1}'.format(row_number, e))
            return None

        device_name = row[1]
        name_len = len(device_name)
        if name_len > 32 or name_len < 1:
            csv_error_logger.error(u'Device in row {0} has invalid name: {1}'.format(row_number, device_name))
            device_name = None

        device_description = row[2]
        if len(device_description) < 1:
            csv_error_logger.error(u'Device in row {0} has invalid description: {1}'.format(row_number,
                                                                                            device_description))
            device_description = None

        device_code = row[3]
        if len(device_code) > 30:
            csv_error_logger.error(u'Device in row {0} has invalid code: {1}'.format(row_number, device_code))
            device_code = None

        if device_code:
            code_exists = Session.query(Device).filter(Device.code == device_code).first()
            if code_exists:
                csv_error_logger.error(
                    u'Code for device in row {0} has duplicate code: {1}'.format(row_number, device_code))
                device_code = None

        try:
            device_expire_date = parser.parse(row[4])
        except Exception as e:
            csv_error_logger.error(u'Device in row {0} has invalid expire date: {1}'.format(row_number, row[4]))
            device_expire_date = None

        status_name = row[5]
        device_status = StatusConstants.get_mapped_status().get(status_name, None)
        if not device_status:
            csv_error_logger.error(u'Device in row {0} has invalid status: {1}'.format(row_number, status_name))
            device_status = None

        return {
            'id': device_id,
            'name': device_name,
            'description': device_description,
            'code': device_code,
            'expire_date': device_expire_date,
            'status': device_status
        }

    def get_parsed_device_content_row(self, row, row_number):
        """
        Method used for getting dict of DeviceContent data from CSV row.
        :param row: CSV Device data row, list
        :param row_number: integer
        :return: dict {
            'id': integer, required,
            'name': string or None for invalid data,
            'description': string or None for invalid data,
            'device_id': Device.id or None for invalid data,
            'expire_date': datetime or None for invalid data,
            'status': integer or None for invalid data
        } or None for error
        """

        if len(row) < 6:
            csv_error_logger.error(u'Device content row {0} has invalid number of columns'.format(row_number))
            return None

        try:
            device_content_id = str(row[0].strip())
            if not device_content_id.isdigit():
                csv_error_logger.error(u'Device content in row {0} has invalid ID: {1}'.format(row_number, row[0]))
                return None
        except Exception as e:
            csv_error_logger.error(u'Device content in row {0} has invalid ID: {1}'.format(row_number, e))
            return None

        device_content_name = row[1]
        name_len = len(device_content_name)
        if name_len > 100 or name_len < 1:
            csv_error_logger.error(u'Device in row {0} has invalid name: {1}'.format(row_number, device_content_name))
            device_content_name = None

        device_content_description = row[2]
        if len(device_content_description) < 1:
            csv_error_logger.error(u'Device in row {0} has invalid description: {1}'.format(row_number,
                                                                                            device_content_description))
            device_content_description = None

        device_id = row[3]
        device = Session.query(Device).filter(Device.id == device_id).first()
        if not device:
            csv_error_logger.error(u'Device content in row {0} has invalid Device ID: {1}'.format(row_number,                                                       device_id))
            device_id = None

        try:
            device_content_expire_date = parser.parse(row[4])
        except Exception as e:
            csv_error_logger.error(u'Device content in row {0} has invalid expire date: {1}'.format(row_number, row[4]))
            device_content_expire_date = None

        status_name = row[5]
        device_content_status = StatusConstants.get_mapped_status().get(status_name, None)
        if not device_content_status:
            csv_error_logger.error(u'Device content in row {0} has invalid status: {1}'.format(row_number, status_name))
            device_content_status = None

        return {
            'id': device_content_id,
            'name': device_content_name,
            'description': device_content_description,
            'device_id': device_id,
            'expire_date': device_content_expire_date,
            'status': device_content_status
        }

    def import_devices_data(self):
        """
        Method used for importing Device data from CSV file.
        """
        csv_file_rows = self.read_csv_file(self.device_file_name)
        if not csv_file_rows:
            return None

        for index, row in enumerate(csv_file_rows, start=1):
            parsed_row = self.get_parsed_device_row(row, index)
            if not parsed_row:
                continue
            device = Session.query(Device)\
                .filter(Device.id == parsed_row['id'])\
                .first()
            if device:
                if device.expire_date < parsed_row['expire_date']:
                    device.code = parsed_row['code']
                    device.name = parsed_row['name']
                    device.description = parsed_row['description']
                    device.expire_date = parsed_row['expire_date']
                    device.status = parsed_row['status']
                    device.date_updated = now()
                    Session.flush()
            else:
                device = Device()
                device.id = parsed_row['id']
                device.name = parsed_row['name']
                device.description = parsed_row['description']
                device.code = parsed_row['code']
                device.expire_date = parsed_row['expire_date']
                device.status = parsed_row['status']
                Session.add(device)
                Session.flush()

    def import_device_content_data(self):
        """
        Method used for importing DeviceContent data from CSV file.
        """
        csv_file_rows = self.read_csv_file(self.content_file_name)
        if not csv_file_rows:
            return None
        for index, row in enumerate(csv_file_rows, start=1):
            parsed_row = self.get_parsed_device_content_row(row, index)
            if not parsed_row:
                continue
            device_content = Session.query(DeviceContent).filter(DeviceContent.id == parsed_row['id']).first()
            if device_content:
                if device_content.expire_date < parsed_row['expire_date']:
                    device_content.name = parsed_row['name']
                    device_content.description = parsed_row['description']
                    device_content.expire_date = parsed_row['expire_date']
                    device_content.status = parsed_row['status']
                    device_content.device_id = parsed_row['device_id']
                    device_content.date_updated = now()
                    Session.flush()
            else:
                device_content = DeviceContent()
                device_content.id = parsed_row['id']
                device_content.device_id = parsed_row['device_id']
                device_content.name = parsed_row['name']
                device_content.description = parsed_row['description']
                device_content.expire_date = parsed_row['expire_date']
                device_content.status = parsed_row['status']
                Session.add(device_content)
                Session.flush()


if __name__ == '__main__':
    with transaction.manager:
        csv_importer = CsvImporter()
        csv_importer.set_settings()
        csv_importer.import_devices_data()
        csv_importer.import_device_content_data()
