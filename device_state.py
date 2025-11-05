import gc

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
    
    def __setattr__(self, name, value):
        # Get old value if exists
        old_value = getattr(self, name, None)

        # Normal attribute set
        super().__setattr__(name, value)

        # If it was changed (not same object)
        if old_value is not None and old_value is not value:
            # Dereference old object
            del old_value
            # Force memory cleanup
            gc.collect()
            # Optional debug log
            print(f"[GC] Released old '{name}', collected memory")

        # Optional trace
        # print(f"[STATE] {name} = {value!r}")