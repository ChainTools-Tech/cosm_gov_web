# Blockchain Proposal Summary Dashboard

## Overview

The Blockchain Proposal Summary Dashboard is a Flask-based web application designed to aggregate and display proposals from various blockchain platforms. It utilizes concurrent processing to fetch and process proposal data, presenting it in an accessible and interactive format for users. This project aims to provide a consolidated view of governance proposals across different chains, making it easier for stakeholders to stay informed and make decisions.

## Features

- **Concurrent Data Processing**: Utilizes ThreadPoolExecutor for efficient data fetching and processing.
- **Dynamic Proposal Aggregation**: Supports multiple blockchain platforms with configurable API endpoints.
- **Interactive UI**: Offers a web interface to view and filter proposals by chain names and IDs.
- **Configurable**: Easy to configure with a TOML file for adding or modifying blockchain platforms.
- **Logging**: Comprehensive logging of application activities and errors for easier debugging and monitoring.

## Requirements

- Python 3.x
- Flask
- Requests
- TOMLKit

## Installation

1. **Clone the repository:**
   
   ```
   git clone https://github.com/yourusername/blockchain-proposal-dashboard.git
   ```

2. **Navigate to the project directory:**

   ```
   cd blockchain-proposal-dashboard
   ```

3. **Install dependencies:**

   ```
   pip install -r requirements.txt
   ```

## Configuration

Before running the application, configure your blockchain platforms and API endpoints in the `config.toml` file. Each chain should specify its `displayname`, `chain-id`, and `api` URL. Optionally, you can customize the `api_gov_prop` path for each chain.

Example `config.toml`:
```toml
[[chains]]
displayname = "ChainName"
chain-id = "chain-1"
api = "http://api.chainname.org"
```

## Running the Application

To start the web server, run:

```
python app.py
```

Navigate to `http://127.0.0.1:5000/` to view the dashboard.


## Running app as a service
```ini
[Unit]
Description=Cosmos Proposal Viewer
After=network.target

[Service]
User=guniapps
Group=guniapps
WorkingDirectory=/home/guniapps/cosmos_gov
Environment="PATH=/home/guniapps/cosmos_gov/venv/bin"
ExecStart=/home/guniapps/cosmos_gov/venv/bin/gunicorn cosmos_gov:app --workers 140 --bind 127.0.0.1:8006 --timeout 180

[Install]
WantedBy=multi-user.target
```


## Usage

- **View Proposals**: Access the `/proposals` route to see the aggregated proposals from configured chains.
- **Filter Proposals**: Use the dropdown menus to filter proposals by chain name or ID.

## Contributing

Contributions are welcome! If you'd like to contribute, please fork the repository and create a pull request with your changes.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
