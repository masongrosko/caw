import os
import unittest
from unittest.mock import patch

from badge_in import _check_required_env_vars_are_present, get_sheet_id_from_url


class TestBadgeLoggingScript(unittest.TestCase):

    @patch.dict(
        os.environ,
        {
            "TYPE": "service_account",
            "PROJECT_ID": "test_project",
            "PRIVATE_KEY_ID": "test_private_key_id",
            "PRIVATE_KEY": "test_private_key",
            "CLIENT_EMAIL": "test_client_email",
            "CLIENT_ID": "test_client_id",
            "AUTH_URI": "test_auth_uri",
            "TOKEN_URI": "test_token_uri",
            "AUTH_PROVIDER_X509_CERT_URL": "test_cert_url",
            "CLIENT_X509_CERT_URL": "test_cert_url",
        },
    )
    def test_validate_env_vars_success(self):
        """Test that all required environment variables are present."""
        try:
            _check_required_env_vars_are_present()
        except EnvironmentError:
            self.fail("validate_env_vars raised EnvironmentError unexpectedly!")

    @patch.dict(os.environ, clear=True)
    def test_validate_env_vars_missing_vars(self):
        """Test that missing environment variables raise EnvironmentError."""
        with self.assertRaises(EnvironmentError):
            _check_required_env_vars_are_present()

    def test_get_sheet_id_from_url_valid(self):
        """Test extracting the sheet ID from a valid Google Sheet URL."""
        url = "https://docs.google.com/spreadsheets/d/12345/edit#gid=0"
        expected_id = "12345"
        sheet_id = get_sheet_id_from_url(url)
        self.assertEqual(sheet_id, expected_id)

    def test_get_sheet_id_from_url_invalid(self):
        """Test extracting the sheet ID from an invalid URL."""
        with self.assertRaises(ValueError):
            get_sheet_id_from_url("https://invalid.url")


if __name__ == "__main__":
    unittest.main()
