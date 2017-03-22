from datetime import datetime


def now():
    return datetime.utcnow()


class StatusConstants(object):
    STATUS_DISABLED = 0
    STATUS_ENABLED = 1
    STATUS_DELETED = -1

    @classmethod
    def get_mapped_status(cls):
        return {
            'disabled': cls.STATUS_DISABLED,
            'enabled': cls.STATUS_ENABLED,
            'deleted': cls.STATUS_DELETED
        }

    @classmethod
    def get_mapped_status_name(cls):
        return {
            cls.STATUS_DISABLED: u'disabled',
            cls.STATUS_ENABLED: u'enabled',
            cls.STATUS_DELETED: u'deleted'
        }