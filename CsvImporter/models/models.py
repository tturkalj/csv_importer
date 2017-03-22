from sqlalchemy import Column, DateTime, Integer, UnicodeText, Unicode, ForeignKey
from sqlalchemy.orm import relationship
from database import Base, Session
from CsvImporter.utility.helper import StatusConstants
from CsvImporter.utility.helper import now


class Device(Base):
    name = Column(Unicode(32), nullable=True)
    description = Column(UnicodeText, nullable=True)
    code = Column(Unicode(30), nullable=True)
    date_created = Column(DateTime, nullable=True, default=now())
    date_updated = Column(DateTime, nullable=True, default=now())
    expire_date = Column(DateTime, nullable=True)
    status = Column(Integer, nullable=True)

    def set_status_from_name(self, status_name):
        self.status = StatusConstants.get_mapped_status()[status_name]

    def get_status_name(self):
        return StatusConstants.get_mapped_status_name()[self.status] if self.status else u'Invalid data'

    def get_name(self):
        return self.name if self.name else u'Invalid data'

    def get_description(self):
        return self.description if self.description else u'Invalid data'

    def get_code(self):
        return self.code if self.code else u'Invalid data'

    def get_date_created(self):
        return self.date_created if self.date_created else u'Invalid data'

    def get_date_updated(self):
        return self.date_updated if self.date_updated else u'Invalid data'

    def get_date_expire_date(self):
        return self.expire_date if self.expire_date else u'Invalid data'


class DeviceContent(Base):
    name = Column(Unicode(100), nullable=True)
    description = Column(UnicodeText, nullable=True)
    date_created = Column(DateTime, nullable=True, default=now())
    date_updated = Column(DateTime, nullable=True, default=now())
    expire_date = Column(DateTime, nullable=True)
    status = Column(Integer, nullable=True)
    device_id = Column(ForeignKey('device.id', ondelete='SET NULL'), nullable=True, index=True)

    device = relationship('Device')

    def set_status_from_name(self, status_name):
        self.status = StatusConstants.get_mapped_status()[status_name]

    def get_status_name(self):
        return StatusConstants.get_mapped_status_name()[self.status] if self.status else u'Invalid data'

    def get_name(self):
        return self.name if self.name else u'Invalid data'

    def get_description(self):
        return self.description if self.description else u'Invalid data'

    def get_date_created(self):
        return self.date_created if self.date_created else u'Invalid data'

    def get_date_updated(self):
        return self.date_updated if self.date_updated else u'Invalid data'

    def get_date_expire_date(self):
        return self.expire_date if self.expire_date else u'Invalid data'

    def get_device_name(self):
        return self.device.name if self.device_id else u'Invalid data'


class ImporterSettings(Base):
    csv_store_path = Column(UnicodeText, nullable=False, default=u'csv_store')
    device_file_name = Column(Unicode(100), nullable=False, default=u'devices.csv')
    content_file_name = Column(Unicode(100), nullable=False, default=u'content.csv')
    default_csv_delimiter = Column(Unicode(1), nullable=False, default=u',')
