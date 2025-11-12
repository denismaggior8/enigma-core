import unittest
import sys
import os
# Add parent folder (where enigmacore.py lives) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from main import process_line
from device_state import DeviceState

class TestEnigmaRotors(unittest.TestCase):


    def setUp(self):
        DeviceState().reset() # ensures fresh state before each test

    def test_at_set_rotor_i_m3(self):
        process_line("AT+ENIGMA=M3")
        out = process_line("AT+ROTOR=0,I,0,0")
        self.assertIn("OK", out)
    
    def test_at_set_rotor_ii_m3(self):
        process_line("AT+ENIGMA=M3")
        out = process_line("AT+ROTOR=0,II,0,0")
        self.assertIn("OK", out)

    def test_at_set_rotor_iii_m3(self):
        process_line("AT+ENIGMA=M3")
        out = process_line("AT+ROTOR=0,III,0,0")
        self.assertIn("OK", out)
    
    def test_at_set_rotor_iv_m3(self):
        process_line("AT+ENIGMA=M3")
        out = process_line("AT+ROTOR=0,IV,0,0")
        self.assertIn("OK", out)

    def test_at_set_rotor_v_m3(self):
        process_line("AT+ENIGMA=M3")
        out = process_line("AT+ROTOR=0,V,0,0")
        self.assertIn("OK", out)

    def test_at_set_rotor_vi_m3(self):
        process_line("AT+ENIGMA=M3")
        out = process_line("AT+ROTOR=0,VI,0,0")
        self.assertIn("OK", out)

    def test_at_set_rotor_vii_m3(self):
        process_line("AT+ENIGMA=M3")
        out = process_line("AT+ROTOR=0,VII,0,0")
        self.assertIn("OK", out)
    
    def test_at_set_rotor_viii_m3(self):
        process_line("AT+ENIGMA=M3")
        out = process_line("AT+ROTOR=0,VIII,0,0")
        self.assertIn("OK", out)

    def test_at_set_rotor_b_m4(self):
        process_line("AT+ENIGMA=M4")
        out = process_line("AT+ROTOR=0,B,0,0")
        self.assertIn("OK", out)

    def test_at_set_rotor_b_m4(self):
        process_line("AT+ENIGMA=M4")
        out = process_line("AT+ROTOR=0,G,0,0")
        self.assertIn("OK", out)

    def test_at_set_unkwnow_rotor_m4(self):
        process_line("AT+ENIGMA=M4")
        out = process_line("AT+ROTOR=0,F,0,0")
        self.assertIn("ERROR", out)

    def test_at_set_and_query_rotor(self):
        process_line("AT+ENIGMA=M3")
        out = process_line("AT+ROTOR=1,I,0,0")
        self.assertIn("OK", out)

        out2 = process_line("AT+ROTOR=1?")
        self.assertIn("+ROTOR: 1,I,0,0", out2)
        self.assertIn("OK", out2)

    def test_at_set_rotor_missing_index_param(self):
        out = process_line("AT+ROTOR=VI,0,0")
        self.assertIn("ERROR", out)

    def test_at_get_rotor_missing_index(self):
        out = process_line("AT+ROTOR?")
        self.assertIn("ERROR", out)

    def test_at_set_rotor_lowercase_param(self):
        out = process_line("AT+ROTOR=1,vi,0,0")
        self.assertIn("ERROR", out)

    def test_at_set_rotor_bad_param_type(self):
        out = process_line("AT+ROTOR=1,VI,NN,0")
        self.assertIn("ERROR", out)

    def test_at_set_negative_rotor_index(self):
        process_line("AT+ENIGMA=M3")
        out = process_line("AT+ROTOR=-1,VI,0,0")
        self.assertIn("ERROR", out)

    def test_at_set_outofbound_rotor_index_m3(self):
        process_line("AT+ENIGMA=M3")
        out = process_line("AT+ROTOR=3,I,0,0")
        self.assertIn("ERROR", out)

    def test_at_set_outofbound_rotor_index_m4(self):
        process_line("AT+ENIGMA=M4")
        out = process_line("AT+ROTOR=4,I,0,0")
        self.assertIn("ERROR", out)


if __name__ == "__main__":
    unittest.main()