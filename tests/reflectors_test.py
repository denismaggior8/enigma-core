import unittest
import sys
import os
# Add parent folder (where enigmacore.py lives) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from main import process_line
from device_state import DeviceState

class TestEnigmaReflectors(unittest.TestCase):


    def setUp(self):
        DeviceState().reset() # ensures fresh state before each test

    def setUp(self):
        # Reset the device state before each test
        DeviceState().reset()

    def test_at_query_reflector_without_model(self):
        """Querying reflector without Enigma model should fail."""
        response = process_line("AT+REFLECTOR?")
        self.assertIn("ERROR", response)

    def test_at_set_reflector_without_model(self):
        """Setting reflector without Enigma model should fail."""
        response = process_line("AT+REFLECTOR=B")
        self.assertIn("ERROR", response)

    def test_at_set_reflector_for_m3(self):
        """Set valid reflector for M3."""
        process_line("AT+ENIGMA=M3")
        out = process_line("AT+REFLECTOR=B")
        self.assertIn("OK", out)
        out = process_line("AT+REFLECTOR?")
        self.assertEquals("+REFLECTOR: B\r\nOK", out)

    def test_at_set_reflector_invalid_for_m3(self):
        """Try to set invalid reflector for M3."""
        process_line("AT+ENIGMA=M3")
        response = process_line("AT+REFLECTOR=CT")
        self.assertIn("ERROR", response)

    def test_at_set_reflector_for_m4(self):
        """Set valid reflector for M4."""
        process_line("AT+ENIGMA=M4")
        out = process_line("AT+REFLECTOR=BT")
        self.assertIn("OK", out)
        out = process_line("AT+REFLECTOR?")
        self.assertEquals("+REFLECTOR: BT\r\nOK", out)

    def test_at_reflector_query_after_set(self):
        """Query reflector after setting it should show correct value."""
        process_line("AT+ENIGMA=M3")
        process_line("AT+REFLECTOR=C")
        response = process_line("AT+REFLECTOR?")
        self.assertIn("+REFLECTOR: C", response)
        self.assertIn("OK", response)

    def test_at_invalid_reflector_name(self):
        """Unknown reflector name must return error."""
        process_line("AT+ENIGMA=M3")
        response = process_line("AT+REFLECTOR=X")
        self.assertIn("ERROR", response)


if __name__ == "__main__":
    unittest.main()