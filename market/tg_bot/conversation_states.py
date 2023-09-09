from enum import Enum, auto


class States(Enum):
    LOGIN = auto()
    PASSWORD = auto()
    CHECK_PASSWORD = auto()
    SHOP_LIST = auto()
    API_KEY = auto()
    SHOP_MENU = auto()
    SHOP_INFO = auto()
    ACTIVATE = auto()
    PRICE_UPDATING = auto()
