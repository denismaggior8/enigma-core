import unittest
import sys
import os
# Add parent folder (where enigmacore.py lives) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from main import process_line

class TestEnigmaCore(unittest.TestCase):
    
    def test_at_basic_at(self):
        self.assertEqual(process_line("AT"), "OK")
   
if __name__ == "__main__":
    unittest.main()