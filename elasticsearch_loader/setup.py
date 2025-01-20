from setuptools import setup, find_packages

setup(
    name="Elasticsearch Connector",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        'pyqt5==5.15.10',
        'elasticsearch==7.10.0'
    ],
    entry_points={
        'qgis.plugins': [
            'Elasticsearch Connector = es_connector:ElasticsearchConnectionDialog'
        ]
    },
)
