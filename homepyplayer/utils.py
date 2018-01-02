import threading

class AtomicBool:
    """An atomic, thread-safe quit flag.

    """

    def __init__(self, initial=True):
        """
            Initialize a new atomic counter to given initial value (default 0).
        """
        self.value = initial
        self._lock = threading.Lock()

    def set(self, newvalue):
        """
            Atomically change the value of the boolean.
        """
        with self._lock:
            self.value = bool(newvalue)

    def get(self):
        with self._lock:
            return self.value