import unittest
from dgca_rules.validator import FDTLValidator
import os
import yaml
import tempfile

class TestFDTLValidator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Create a temporary config for testing
        cls.config_path = 'test_config.yaml'
        test_config = {
            'dgca_fdtl': {
                'max_daily_flight_time': 8.0,
                'max_daily_duty_period': 12.0,
                'min_rest_period': 12.0,
                'max_consecutive_night_duties': 2,
                'mandatory_night_rest_hours': 56.0,
                'weekly_flight_time_limit': 35.0
            }
        }
        with open(cls.config_path, 'w') as f:
            yaml.dump(test_config, f)
        cls.validator = FDTLValidator(config_path=cls.config_path)

    @classmethod
    def tearDownClass(cls):
        if os.path.exists(cls.config_path):
            os.remove(cls.config_path)

    def test_daily_limit_compliant(self):
        pilot = {"daily_flight_hours": 4}
        flight = {"duration_hours": 2}
        compliant, _ = self.validator.validate_assignment(pilot, flight)
        self.assertTrue(compliant)

    def test_daily_limit_exceeded(self):
        pilot = {"daily_flight_hours": 7}
        flight = {"duration_hours": 2}
        compliant, reason = self.validator.validate_assignment(pilot, flight)
        self.assertFalse(compliant)
        self.assertIn("Exceeds max daily flight time", reason)

    def test_night_duty_violation(self):
        pilot = {
            "consecutive_night_duties": 2,
            "hours_since_last_rest": 24
        }
        flight = {"duration_hours": 2}
        compliant, reason = self.validator.validate_assignment(pilot, flight)
        self.assertFalse(compliant)
        self.assertIn("consecutive night duties", reason)

    def test_weekly_limit_exceeded(self):
        pilot = {"weekly_flight_hours": 34}
        flight = {"duration_hours": 2}
        compliant, reason = self.validator.validate_assignment(pilot, flight)
        self.assertFalse(compliant)
        self.assertIn("weekly flight limit", reason)

    def test_config_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            FDTLValidator(config_path="nonexistent.yaml")

    def test_invalid_config_missing_section(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump({"other": "data"}, f)
            temp_path = f.name
        try:
            with self.assertRaises(KeyError):
                FDTLValidator(config_path=temp_path)
        finally:
            os.unlink(temp_path)

if __name__ == '__main__':
    unittest.main()
