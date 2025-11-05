import unittest
import sys
import os
# Add parent folder (where enigmacore.py lives) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import process_line
from device_state import DeviceState

class TestEnigmaCore(unittest.TestCase):


    def setUp(self):
        DeviceState().reset()   # ensures fresh state before each test

    def test_at_set_enigma_m3(self):
        self.assertEqual(process_line("AT+ENIGMA=M3"), "OK")

    def test_at_set_and_get_enigma_m3(self):
        process_line("AT+ENIGMA=M3")
        self.assertEqual(process_line("AT+ENIGMA?"), "+ENIGMA: M3\r\nOK")

    def test_at_enigma_query(self):
        self.assertEqual(process_line("AT+ENIGMA?"), "+ENIGMA: NONE\r\nOK")


if __name__ == "__main__":
    unittest.main()