import unittest
import sys
import os
# Add parent folder (where enigmacore.py lives) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src")))
from enigmacore.main import process_line, _COMMANDS

class TestEnigmaCoreSystem(unittest.TestCase):
    
    def test_at_basic(self):
        self.assertEqual(process_line("AT"), "OK")
    
    def test_at_help(self):
        output = process_line("AT+HELP")

        # Ensure HELP succeeded
        self.assertIn("OK", output)

        # Extract registered commands
        registered = sorted(_COMMANDS.keys())

        # Ensure every command name appears in HELP output
        for cmd in registered:
            self.assertIn(cmd, output, msg=f"HELP missing command: {cmd}")

        # Optionally: ensure no *extra* unknown commands appear
        # (e.g. if typo or debug command leaked)
        for line in output.splitlines():
            if line.startswith("AT+"):
                self.assertIn(line.strip(), registered)
   
if __name__ == "__main__":
    unittest.main()