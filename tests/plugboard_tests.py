import unittest
import sys
import os
# Add parent folder (where enigmacore.py lives) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from enigmacore.main import process_line
from enigmacore.device_state import DeviceState

class TestEnigmaPlugboard(unittest.TestCase):


    def setUp(self):
        DeviceState().reset() # ensures fresh state before each test

    def test_at_set_and_query_plugboard_m3(self):
        process_line("AT+ENIGMA=M3")
        out = process_line("AT+PLUGBOARD=A,Z")
        self.assertEqual(process_line("AT+PLUGBOARD?"), "+PLUGBOARD: zbcdefghijklmnopqrstuvwxya\r\nOK")
    
if __name__ == "__main__":
    unittest.main()