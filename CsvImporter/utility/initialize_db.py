import transaction
from CsvImporter.models.database import Session, init_db
from CsvImporter.models.models import ImporterSettings


def initialize():
    init_db()
    with transaction.manager:
        settings = Session.query(ImporterSettings).first()
        if not settings:
            settings = ImporterSettings()
            settings.id = 1
            Session.add(settings)
            Session.flush()

if __name__ == '__main__':
    initialize()
