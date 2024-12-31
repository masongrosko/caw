# Badge Logging System

This script is used to log RFID badge scans into a Google Sheet. It connects to the Google Sheets API, reads badge data via an RFID reader, and stores the badge ID and timestamp in a specified Google Sheet. The system is designed to be run on a Raspberry Pi, but can be tested in a mock environment.

## Setup

### Requirements

Before running the script, ensure that the following requirements are met:

1. **Python** 3.x (Tested with Python 3.12+)
1. **Raspberry Pi** (for hardware) or mock environment (for testing)
1. **Google Sheets API credentials**

### Installation

1. Clone or download the repository.
1. Install the required Python libraries:

   ```bash
   cd path/to/this/dir
   pip install -r requirements-badge-in.txt
   ```

1. Create a Google Cloud project and enable the Google Sheets API. [Example from youtube](https://www.youtube.com/watch?v=zCEJurLGFRk). We need the service account credentials. Once you have those you are done.

1. Download the service account credentials as a JSON file and store them in a `.env` file in the same dir as this script.

1. Set up the following files:

    * **.env**: Store your Google Cloud credentials in this file.
    * **config.yaml**: Configure your Google Sheets details (URL, worksheet name, etc.).

### Environment Configuration

1. **.env**: This file should contain your Google Sheets API credentials in the following format:

    ```.env
    TYPE = "<REDACTED>"
    PROJECT_ID = "<REDACTED>"
    PRIVATE_KEY_ID = "<REDACTED>"
    PRIVATE_KEY = "<REDACTED>"
    CLIENT_EMAIL = "<REDACTED>"
    CLIENT_ID = "<REDACTED>"
    AUTH_URI = "<REDACTED>"
    TOKEN_URI = "<REDACTED>"
    AUTH_PROVIDER_X509_CERT_URL = "<REDACTED>"
    CLIENT_X509_CERT_URL = "<REDACTED>"
    UNIVERSE_DOMAIN = "<REDACTED>"
    ```

1. **config.yaml**: Configure the connection to your Google Sheet and define the columns used in the worksheet:

    ```yaml
    google_sheet:
      scopes:
        - "https://www.googleapis.com/auth/spreadsheets"
      url: "https://docs.google.com/spreadsheets/d1GUc7sXY-M_IPpDB2TTLUDPQ7MoDRd_ubD4lKkDCjopg/editgid=0#gid=0"
      worksheet_name: "badge_logs"

    worksheet:
      header_row:
        - "id"
        - "date"
    ```

### Running the script

1. Start the script: To run the badge logging system, simply execute the script:

    ```bash
    python badge_logging.py
    ```

1. **Functionality**: The script will continuously monitor for RFID scans, log the badge ID and timestamp to your Google Sheet, and display information in the console. It checks for errors in the process and logs relevant information for debugging.

    * **Logging**: Logs are stored using Python's logging module and can be viewed in the console.
    * **Google Sheets**: Badge logs are appended to the configured Google Sheets worksheet (badge_logs by default).
