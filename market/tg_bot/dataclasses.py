from dataclasses import dataclass


@dataclass
class ShopInfo:
    id: int
    name: str


@dataclass
class Navigation:
    limit: int
    offset: int
