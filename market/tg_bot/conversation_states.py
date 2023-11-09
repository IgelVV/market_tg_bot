from enum import Enum, auto


class States(Enum):
    """States for ConversationHandlers."""
    SUBSCRIPTION = auto()
    # ADD_SHOP = auto()
    UNLINK_SHOP = auto()
    SHOP_LIST = auto()
    SHOP_MENU = auto()
    SHOP_INFO = auto()
    ACTIVATE = auto()
    PRICE_UPDATING = auto()
