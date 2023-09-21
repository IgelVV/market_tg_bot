from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ShopInfo:
    """Represents Shop model for using in bot handlers."""
    id: int
    name: str
    slug: Optional[str] = field(default=None, repr=False)
    api_key: Optional[str] = field(default=None, repr=False)
    vendor_name: Optional[str] = field(default=None, repr=False)
    is_active: Optional[bool] = field(default=None, repr=False)
    update_prices: Optional[bool] = field(default=None, repr=False)
    individual_updating_time: Optional[bool] = field(default=None, repr=False)


@dataclass
class Navigation:
    """Contains information for page navigation."""
    limit: int
    offset: int
