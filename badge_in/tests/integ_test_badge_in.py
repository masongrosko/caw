import unittest
from unittest.mock import MagicMock, patch

from badge_in import initialize_badge_logging_system, log_badge


def row_count(worksheet):
    return len(worksheet.col_values(1))


class IntegTestBadgeLoggingScript(unittest.TestCase):

    def test_log_badge(self):
        """Test we actually add rows to db."""
        fake_id = "123456"

        with patch("badge_in.get_rfid_reader") as mock_rfid_reader:
            mock_reader_instance = MagicMock()
            mock_reader_instance.read_id.side_effect = [
                fake_id,  # First call returns a valid ID
                Exception(
                    "read error on second call"
                ),  # Second call raises an exception
            ]
            mock_rfid_reader.return_value = mock_reader_instance

            badge_logs, reader = initialize_badge_logging_system()

        starting_rows = row_count(badge_logs)

        # Run
        log_badge(badge_logs=badge_logs, reader=reader)

        # Verify that append_row was called
        self.assertGreater(
            row_count(badge_logs),
            starting_rows,
            "Row count should increase after logging a badge.",
        )
        self.assertEqual(
            badge_logs.row_values(row_count(badge_logs))[0],
            fake_id,
            f"Expected the logged badge ID to be {fake_id}, but got"
            f" {badge_logs.row_values(row_count(badge_logs))[0]}.",
        )


if __name__ == "__main__":
    unittest.main()
