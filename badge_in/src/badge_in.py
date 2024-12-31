import datetime
import logging
import os
import time
from pathlib import Path

import gspread
import yaml
from dotenv import find_dotenv, load_dotenv
from google.oauth2.service_account import Credentials
from gspread.utils import ValueInputOption

# Set up logging
logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

try:
    from mfrc522 import SimpleMFRC522
except ModuleNotFoundError:
    LOGGER.error(
        "Required raspberry pi packages not installed. If you are running on a"
        " raspberry pi, you need to rerun installing the required packages."
    )
    from unittest.mock import MagicMock, patch

    MockRPi = MagicMock()
    spidev = MagicMock()
    modules = {
        "RPi": MockRPi,
        "RPi.GPIO": MockRPi.GPIO,
        "spidev": spidev,
    }
    with patch.dict("sys.modules", modules):
        from mfrc522 import SimpleMFRC522

# Package folder
package_folder = Path(__file__).parents[1]

# Load environment variables from .env file
dot_env_file = find_dotenv()
if not dot_env_file:
    dot_env_file = package_folder / ".env"
load_dotenv(dot_env_file)


# Load the configuration from config.yaml
with open(package_folder / "config.yaml", "r") as f:
    config = yaml.safe_load(f)

# Get the configuration values
SCOPES = config["google_sheet"]["scopes"]
GOOGLE_SHEET_URL = config["google_sheet"]["url"]
WORKSHEET_NAME = config["google_sheet"]["worksheet_name"]
HEADER_ROW = config["worksheet"]["header_row"]


def get_google_creds() -> Credentials:
    """Load service account credentials from environment vars."""
    _check_required_env_vars_are_present()
    return Credentials.from_service_account_info(
        info={
            "type": os.environ.get("TYPE"),
            "project_id": os.environ.get("PROJECT_ID"),
            "private_key_id": os.environ.get("PRIVATE_KEY_ID"),
            "private_key": os.environ.get("PRIVATE_KEY"),
            "client_email": os.environ.get("CLIENT_EMAIL"),
            "client_id": os.environ.get("CLIENT_ID"),
            "auth_uri": os.environ.get("AUTH_URI"),
            "token_uri": os.environ.get("TOKEN_URI"),
            "auth_provider_x509_cert_url": os.environ.get(
                "AUTH_PROVIDER_X509_CERT_URL"
            ),
            "client_x509_cert_url": os.environ.get("CLIENT_X509_CERT_URL"),
            "universe_domain": os.environ.get("UNIVERSE_DOMAIN"),
        },
        scopes=SCOPES,
    )


def _check_required_env_vars_are_present() -> None:
    """Make sure all values are provided"""
    required_env_vars = [
        "TYPE",
        "PROJECT_ID",
        "PRIVATE_KEY_ID",
        "PRIVATE_KEY",
        "CLIENT_EMAIL",
        "CLIENT_ID",
        "AUTH_URI",
        "TOKEN_URI",
        "AUTH_PROVIDER_X509_CERT_URL",
        "CLIENT_X509_CERT_URL",
    ]
    missing_vars = [var for var in required_env_vars if not os.environ.get(var)]
    if missing_vars:
        raise EnvironmentError(
            f"Missing environment variables: {', '.join(missing_vars)}"
        )


def get_sheet_id_from_url(url: str) -> str:
    """Extract the Google Sheet ID from its URL."""
    if "/d/" not in url:
        raise ValueError(
            "Invalid Google Sheet URL, expected format of"
            " 'https://docs.google.com/spreadsheets/d/<sheet_id>/...'"
        )
    try:
        return url.split("/d/")[-1].split("/")[0]
    except IndexError:
        raise ValueError("Invalid Google Sheet URL.")


def get_badge_logs_sheet(
    spreadsheet: gspread.spreadsheet.Spreadsheet,
) -> gspread.worksheet.Worksheet:
    """Get the badge logs sheet."""
    # If it does not exist, create it
    if WORKSHEET_NAME not in [ws.title for ws in spreadsheet.worksheets()]:
        LOGGER.info(
            "No worksheet found with name '{WORKSHEET_NAME}', creating a new one."
        )
        spreadsheet.add_worksheet(title=WORKSHEET_NAME, rows=1, cols=len(HEADER_ROW))
        spreadsheet.worksheet(WORKSHEET_NAME).append_row(HEADER_ROW)
    return spreadsheet.worksheet(WORKSHEET_NAME)


def log_badge(badge_logs: gspread.worksheet.Worksheet, reader: SimpleMFRC522) -> None:
    """Log badge event."""
    try:
        badge_id: str = str(reader.read_id())
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        badge_logs.append_row(
            [badge_id, timestamp], value_input_option=ValueInputOption.user_entered
        )

        LOGGER.info(f"Logged badge ID: {badge_id} at {timestamp}")
    except Exception as e:
        LOGGER.info(f"Error logging badge: {e}")


def get_rfid_reader() -> SimpleMFRC522:
    """Largely unnecessary, but helps for testing."""
    return SimpleMFRC522()


def initialize_badge_logging_system() -> (
    tuple[gspread.worksheet.Worksheet, SimpleMFRC522]
):
    """Get google worksheet connection and reader initialized."""
    creds = get_google_creds()
    client = gspread.auth.authorize(creds)
    sheet_id = get_sheet_id_from_url(GOOGLE_SHEET_URL)
    spreadsheet = client.open_by_key(sheet_id)
    badge_logs = get_badge_logs_sheet(spreadsheet)

    # Initialize RFID reader
    reader = get_rfid_reader()

    return badge_logs, reader


def main() -> None:
    """The main function to run."""
    try:
        badge_logs, rfid_reader = initialize_badge_logging_system()
    except Exception as e:
        LOGGER.error(f"Error initializing badge logging system: {e}")
        return None

    while True:
        log_badge(badge_logs, rfid_reader)
        time.sleep(0.1)


if __name__ == "__main__":
    main()

    # TODO: raspberry pi
    # TODO: Determine ins and outs.
    # TODO: Handle missed badging?
    # TODO: Flag probable missed badging
