from setuptools import setup
from CsvImporter import __version__


setup(
    name='CsvImporter',
    version=__version__,
    packages=['CsvImporter'],
    include_package_data=True,
)