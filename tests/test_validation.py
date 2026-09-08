import unittest

from add import validation


class ValidationTests(unittest.TestCase):
    def test_validation_helper_accepts_valid_deadlines(self):
        self.assertTrue(validation.is_valid_date("09/09/2026"))
        self.assertTrue(validation.is_valid_time("18:30"))
        self.assertTrue(validation.has_valid_deadline("09/09/2026", "18:30"))

    def test_validation_helper_rejects_invalid_inputs(self):
        self.assertFalse(validation.is_valid_date("2026-09-09"))
        self.assertFalse(validation.is_valid_time("18:30 PM"))
        self.assertFalse(validation.has_valid_deadline("", "18:30"))


if __name__ == "__main__":
    unittest.main()
