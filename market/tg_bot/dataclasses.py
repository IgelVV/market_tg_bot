from dataclasses import dataclass
from typing import Optional


@dataclass
class ShopInfo:
    """Represents Shop model for using in bot handlers."""
    id: int
    name: str
    slug: Optional[str] = None
    api_key: Optional[str] = None
    vendor_name: Optional[str] = None
    is_active: Optional[bool] = None
    stop_updated_price: Optional[bool] = None
    individual_updating_time: Optional[bool] = None


@dataclass
class Navigation:
    """Contains information for page navigation."""
    limit: int
    offset: int
