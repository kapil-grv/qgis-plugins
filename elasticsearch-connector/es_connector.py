import json
from qgis.core import QgsVectorLayer, QgsProject, QgsFeature, QgsGeometry, QgsField
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import QVariant
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from .ui_dialog import Ui_Dialog

import sys
import os

# Add the python/ directory to sys.path
plugin_path = os.path.dirname(__file__)
sys.path.insert(0, os.path.join(plugin_path, "python"))

from elasticsearch import Elasticsearch, exceptions

class ElasticsearchPlugin:
    """QGIS Plugin Implementation."""
    
    def __init__(self, iface):
        """Constructor."""
        self.iface = iface
        self.dialog = None
        self.connection = None
        self.plugin_dir = os.path.dirname(__file__)
        
        # Initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        
        # Declare instance attributes
        self.actions = []
        self.menu = 'Elasticsearch Connector'
        self.toolbar = self.iface.addToolBar('Elasticsearch Connector')
        self.toolbar.setObjectName('ElasticsearchConnector')

    def add_action(self, icon_path, text, callback, enabled_flag=True,
                  add_to_menu=True, add_to_toolbar=True, status_tip=None,
                  whats_this=None, parent=None):
        """Add a toolbar icon to the toolbar."""
        icon = QIcon(icon_path) if icon_path else QIcon()
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(self.menu, action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""
        icon_path = os.path.join(plugin_path, 'icons', 'icon.png')
        self.add_action(
            icon_path,
            text='Elasticsearch Connector',
            callback=self.run,
            parent=self.iface.mainWindow(),
            status_tip='Connect to Elasticsearch'
        )
        
        # Initialize the dialog
        self.dialog = ElasticsearchConnectionDialog(self.iface)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu('Elasticsearch Connector', action)
            self.iface.removeToolBarIcon(action)
        
        # Remove the toolbar
        del self.toolbar
            
        # Clean up dialog and connection
        if self.dialog:
            self.dialog.close()
            self.dialog = None
        if self.connection:
            self.connection.close()
            self.connection = None

    def run(self):
        """Run method that performs all the real work"""
        if self.dialog:
            self.dialog.show()
            result = self.dialog.exec_()
            return result

class ElasticsearchConnectionDialog(QDialog, Ui_Dialog):
    def __init__(self, iface):
        """Initialize the dialog window."""
        super().__init__()
        self.setupUi(self)
        self.iface = iface
        self.connection = None

        # Connect buttons to their functions
        self.pushButton.clicked.connect(self.connect_to_elasticsearch)
        self.pushButton_2.clicked.connect(self.run_query)

    def connect_to_elasticsearch(self):
        """Establish connection to Elasticsearch server"""
        host = self.Host.text()
        port = self.Host_2.text()
        index = self.Host_3.text()
        username = self.label_7.text() # Get the Username (optional)
        password = self.label_6.text() # Get the Password (optional)

        if not all([host, port, index]):
            self.textBrowser.setText("All fields are required.")
            return

        try:
            # Create connection configuration
            es_config = {
                'hosts': [f"http://{host}:{port}"]
            }

            # Add basic authentication if credentials are provided
            if username and password:
                es_config['basic_auth'] = (username, password)

            # Create Elasticsearch client with authentication
            es = Elasticsearch(**es_config)
            
            # Test connection
            if es.ping():
                self.connection = es
                self.label.setText(f"Connected to {host}:{port}, Index: {index}")
            else:
                self.label.setText("Failed to connect to Elasticsearch.")
        except exceptions.ConnectionError as e:
            self.textBrowser.setText(f"Connection failed: {str(e)}")
        except Exception as e:
            self.textBrowser.setText(f"Unexpected error: {str(e)}")

    def run_query(self):
        """Execute the Elasticsearch query and load results"""
        if not self.connection:
            self.textBrowser.setText("Please connect to Elasticsearch first")
            return

        query = self.textEdit.toPlainText()
        if not query:
            self.textBrowser.setText("Please enter a query")
            return

        try:
            # Parse the query string as JSON
            query_json = json.loads(query)
            index = self.Host_3.text()

            # Execute the search query
            response = self.connection.search(index=index, body=query_json)
            
            # Check if the response is a wrapped ObjectApiResponse
            if hasattr(response, 'body'):
                # If the response is wrapped, get the actual JSON body
                response = response.body

            # Now, response is a dictionary and can be used as JSON
            self.load_data(response)
            self.textBrowser.setText(f"Query executed successfully, with response: \n\n\n{json.dumps(response, indent=4)}")

        except json.JSONDecodeError:
            self.textBrowser.setText("Invalid JSON query format")
        except Exception as e:
            self.textBrowser.setText(f"Error running query: {str(e)}")

    def display_response(self, response):
        """Display the entire Elasticsearch response in textBrowser."""
        formatted_response = json.dumps(response, indent=4)  # Pretty format the response
        self.textBrowser.setText(formatted_response)  # Set the formatted response to the textBrowser

        # Optionally, load data into QGIS if desired (in addition to displaying the response)
        self.load_data(response)

    def load_data(self, response):
        """Load the Elasticsearch query results as QGIS features."""
        if not response.get('hits', {}).get('hits', []):
            self.textBrowser.append("No results found")
            return

        features = []
        layer = None

        try:
            # Initialize the geometry type and fields dynamically
            first_hit = response['hits']['hits'][0]
            first_geom_type = first_hit['_source'].get('geometry', {}).get('type', '').upper()

            # Map geometry type to QGIS layer type
            geom_type_map = {
                'POINT': "Point?crs=EPSG:4326",
                'LINESTRING': "LineString?crs=EPSG:4326",
                'POLYGON': "Polygon?crs=EPSG:4326",
                'MULTIPOINT': "MultiPoint?crs=EPSG:4326",
                'MULTILINESTRING': "MultiLineString?crs=EPSG:4326",
                'MULTIPOLYGON': "MultiPolygon?crs=EPSG:4326"
            }
            layer_type = geom_type_map.get(first_geom_type, "Point?crs=EPSG:4326")
            layer = QgsVectorLayer(layer_type, "Elasticsearch Results", "memory")
            provider = layer.dataProvider()

            # Collect all unique fields from the ES response
            fields = set()
            for hit in response['hits']['hits']:
                fields.update(hit['_source'].keys())

            # Add fields dynamically to the layer
            for field in fields:
                provider.addAttributes([QgsField(field, QVariant.String)])
            layer.updateFields()

            # Process each hit
            for hit in response['hits']['hits']:
                source = hit['_source']
                if 'geometry' not in source:
                    continue

                try:
                    # Convert geometry to WKT
                    geometry = source['geometry']
                    wkt = self.geometry_to_wkt(geometry)
                    if not wkt:
                        continue

                    feature = QgsFeature()
                    feature.setGeometry(QgsGeometry.fromWkt(wkt))

                    # Set attributes dynamically
                    attributes = [str(source.get(field, '')) for field in fields]
                    feature.setAttributes(attributes)

                    features.append(feature)
                except Exception as e:
                    self.textBrowser.append(f"Error processing feature: {str(e)}")
                    continue

            # Add features to the layer
            if features:
                provider.addFeatures(features)
                layer.updateExtents()
                QgsProject.instance().addMapLayer(layer)
                self.textBrowser.append(f"Loaded {len(features)} features with all fields as attributes.")
            else:
                self.textBrowser.append("No valid features found.")

        except Exception as e:
            self.textBrowser.append(f"Error creating layer: {str(e)}")
            if layer:
                QgsProject.instance().removeMapLayer(layer.id())

    def geometry_to_wkt(self, geometry):
        """Convert GeoJSON geometry to WKT format."""
        try:
            if not isinstance(geometry, dict):
                return ""

            geom_type = geometry.get('type', '').upper()
            coordinates = geometry.get('coordinates', [])

            if geom_type == 'POINT' and len(coordinates) >= 2:
                return f"POINT({coordinates[0]} {coordinates[1]})"
            
            elif geom_type == 'LINESTRING':
                coords = ' '.join([f"{x} {y}" for x, y in coordinates])
                return f"LINESTRING({coords})"
            
            elif geom_type == 'POLYGON':
                outer_ring = ' '.join([f"{x} {y}" for x, y in coordinates[0]])
                return f"POLYGON(({outer_ring}))"
            
            elif geom_type == 'MULTIPOINT':
                points = ' '.join([f"({x} {y})" for x, y in coordinates])
                return f"MULTIPOINT({points})"
            
            elif geom_type == 'MULTILINESTRING':
                lines = ', '.join([f"({', '.join([f'{x} {y}' for x, y in line])})" for line in coordinates])
                return f"MULTILINESTRING({lines})"
            
            elif geom_type == 'MULTIPOLYGON':
                polygons = ', '.join([
                    '(' + ', '.join([
                        '(' + ', '.join([f"{x} {y}" for x, y in ring]) + ')'
                        for ring in polygon
                    ]) + ')'
                    for polygon in coordinates
                ])
                return f"MULTIPOLYGON({polygons})"
            return ""

        except Exception:
            return ""
