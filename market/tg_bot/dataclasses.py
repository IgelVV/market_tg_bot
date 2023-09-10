from dataclasses import dataclass
from typing import Optional


@dataclass
class ShopInfo:
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
    limit: int
    offset: int
