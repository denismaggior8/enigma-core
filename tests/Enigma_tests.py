import unittest
import sys
import os
# Add parent folder (where enigmacore.py lives) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src/enigmacore")))
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
        
    def test_at_set_enigma_m4(self):
        self.assertEqual(process_line("AT+ENIGMA=M4"), "OK")

    def test_at_set_and_get_enigma_m4(self):
        process_line("AT+ENIGMA=M4")
        self.assertEqual(process_line("AT+ENIGMA?"), "+ENIGMA: M4\r\nOK")

    def test_at_enigma_query_null(self):
        self.assertEqual(process_line("AT+ENIGMA?"), "+ENIGMA: NONE\r\nOK")

    # echo "AT+ENIGMA=M3\r\nAT+REFLECTOR=B\r\nAT+ROTOR=0,I,0,0\r\nAT+ROTOR=1,II,0,0\r\nAT+ROTOR=2,III,0,0\r\nciao" | python main.py
    def test_at_enigma_cypher_III_m3(self):
        process_line("AT+ENIGMA=M3")
        process_line("AT+ROTOR=0,I,0,0")
        process_line("AT+ROTOR=1,II,0,0")
        process_line("AT+ROTOR=2,III,0,0")
        process_line("AT+REFLECTOR=B")
        self.assertEqual(process_line("ciao"), "kjtq\r\nOK")


if __name__ == "__main__":
    unittest.main()