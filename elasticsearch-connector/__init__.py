# __init__.py
def classFactory(iface):
    """Load ElasticsearchPlugin class.
    :param iface: A QGIS interface instance.
    """
    from .es_connector import ElasticsearchPlugin
    return ElasticsearchPlugin(iface)
