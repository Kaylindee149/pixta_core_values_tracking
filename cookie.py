import extra_streamlit_components as stx

from threading import Lock


class SingletonMeta(type):
    _instances = {}

    _lock: Lock = Lock()
    """
    We now have a lock object that will be used to synchronize threads during
    first access to the Singleton.
    """

    def __call__(cls, *args, **kwargs):
        with cls._lock:
            if cls not in cls._instances:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
        return cls._instances[cls]


class CookieManagerSingleton(metaclass=SingletonMeta):
    def __init__(self):
        # Initialization code here
        self.cookie_manager = stx.CookieManager()
