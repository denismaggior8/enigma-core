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

    def test_set_and_query_rotor(self):
        out = process_line("AT+ROTOR=1,VI,0,0")
        # SET returns OK (no payload)
        self.assertIn("OK", out)

        out2 = process_line("AT+ROTOR=1?")
        self.assertIn("+ROTOR: 1,VI,0,0", out2)
        self.assertIn("OK", out2)

    def test_missing_index_set(self):
        out = process_line("AT+ROTOR=VI,0,0")
        self.assertIn("ERROR", out)

    def test_missing_index_query(self):
        out = process_line("AT+ROTOR?")
        self.assertIn("ERROR", out)

    def test_lowercase_rejected(self):
        out = process_line("AT+ROTOR=1,vi,0,0")
        self.assertIn("ERROR", out)

    def test_bad_number_param(self):
        out = process_line("AT+ROTOR=1,VI,NN,0")
        self.assertIn("ERROR", out)



if __name__ == "__main__":
    unittest.main()