# Elasticsearch Connector with PyQt5

This project is a PyQt5-based graphical user interface (GUI) for connecting to an Elasticsearch instance, running queries, and displaying the results in a QGIS-compatible format. The application supports optional password authentication for enhanced security.

---

## Features

1. **Dynamic Elasticsearch Connection**:
   - Connect to Elasticsearch by specifying the host, port, index, and optional password.
   - Validate the connection and display connection status.

2. **Query Execution**:
   - Run DSL queries directly from the GUI.
   - View raw query results in the application.

3. **QGIS Integration**:
   - Load results as QGIS-compatible features, supporting multiple geometry types.
   - Dynamically handle fields and attributes from Elasticsearch responses.

4. **Intuitive UI**:
   - User-friendly interface with fields for host, port, index, and password.
   - Text area for entering DSL queries.
   - Log viewer for status and error messages.

---

## Requirements

### Python Packages:
- PyQt5
- elasticsearch
- qgis.core (QGIS Python bindings)

### Environment:
- Python 3.7+
- QGIS installation for Python bindings.

---

## Usage

Download or generate `elasticsearch-connector.zip` by cloning the repo and install it using Plugin Manager in QGIS

Use the GUI to enter the following information:
   - **Host**: Elasticsearch host (e.g., `127.0.0.1`).
   - **Port**: Elasticsearch port (e.g., `9200`).
   - **Index**: Elasticsearch index name (e.g., `index_name`).
   - **Password**: (Optional) Password for Elasticsearch authentication.

Click **Connect** to validate the connection.
Enter a DSL query in the "DSL Query" text area and click **Run Query** to fetch results.

### Loading Data into QGIS:

- Successfully fetched data will be processed and added as layers in QGIS, with attributes populated from the Elasticsearch response.

---

## File Structure

- `main.py`: Entry point for the application.
- `es_connector.py`: Logic for connecting to Elasticsearch and processing query results.
- `es_connector.ui`: PyQt5 UI file.
- `README.md`: Project documentation.

---

## Sample Elasticsearch Query

Default query loaded in the UI:
```json
{
  "size": 100,
  "query": {
    "match_all": {}
  }
}
```
You can modify this query in the "DSL Query" text area.

---

## Known Issues

1. Ensure the Elasticsearch instance is running and accessible.
2. If using password authentication, verify credentials.
3. QGIS bindings must be properly installed and configured.

---

## Contributing

Contributions are welcome! Please follow these steps:
1. Fork the repository.
2. Create a feature branch (`git checkout -b feature-name`).
3. Commit your changes (`git commit -m 'Add feature'`).
4. Push to the branch (`git push origin feature-name`).
5. Open a pull request.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.

---

## Acknowledgments

- Built with PyQt5 and Elasticsearch Python client.
- QGIS integration powered by its Python bindings.

---

For questions or issues, feel free to open an issue in the repository or contact the maintainer.

