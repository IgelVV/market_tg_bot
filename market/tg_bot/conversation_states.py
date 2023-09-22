from enum import Enum, auto


class States(Enum):
    """States for ConversationHandlers."""
    # login conversation
    LOGIN = auto()
    PASSWORD = auto()
    CHECK_PASSWORD = auto()
    API_KEY = auto()
    # main conversation
    ADMIN_MENU = auto()
    SELLER_MENU = auto()
    ADD_SHOP = auto()
    UNLINK_SHOP = auto()
    SHOP_LIST = auto()
    SHOP_MENU = auto()
    SHOP_INFO = auto()
    ACTIVATE = auto()
    PRICE_UPDATING = auto()
