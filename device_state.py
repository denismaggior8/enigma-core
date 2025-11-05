import gc

class DeviceState:
    _instance = None   # class-level storage

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.__initialized = False
        return cls._instance

    
    def __init__(self):
        # Prevent "__init__" from running more than once,
        # unless reset() explicitly allows it.
        if self.__initialized:
            return
        self.__initialized = True

        self.enigma = None
        self.etw = None
        self.plugboard = None
        self.rotor1 = None
        self.rotor2 = None
        self.rotor3 = None
        self.reflector = None

    def reset(self):
        """Wipe all state and reinitialize singleton."""
        self.__initialized = False
        # Clear all current attributes except internals
        for k in list(self.__dict__.keys()):
            if not k.startswith("_"):
                del self.__dict__[k]
        # Force __init__ again
        self.__init__()

        # Optional: free memory (works on MicroPython too)
        try:
            import gc
            gc.collect()
        except ImportError:
            pass

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
            # print(f"[GC] Released old '{name}', collected memory")

        # Optional trace
        # print(f"[STATE] {name} = {value!r}")