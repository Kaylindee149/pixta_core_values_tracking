from streamlit_cookies_controller import CookieController


class SingletonMeta(type):
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance


class CookieManagerSingleton(metaclass=SingletonMeta):
    def __init__(self):
        # Initialization code here
        self.cookie_manager = CookieController()
