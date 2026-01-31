from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class GeoLocation:
    latitude: float
    longitude: float


@dataclass
class Building:
    address: str
    geolocation: GeoLocation
    id: int
    created_at: datetime | None = None


@dataclass
class Activity:
    name: str
    id: int
    parent_id: int | None = None


@dataclass
class Organization:
    name: str
    id: int
    building_id: int
    building: Building
    phones: list[str] = field(default_factory=list)
    activities: list[Activity] = field(default_factory=list)
    created_at: datetime | None = None
    updated_at: datetime | None = None
