

class DeviceState:
    _instance = None   # class-level storage

    def __init__(self):
        self.enigma = None
        self.etw = None
        self.plugboard = None
        self.rotor1 = None
        self.rotor2 = None
        self.rotor3 = None
        self.reflector = None

    @classmethod
    def get(cls):
        """Return the singleton instance (create on first access)."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance