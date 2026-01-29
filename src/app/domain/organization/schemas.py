from typing import Annotated

from pydantic import BaseModel, BeforeValidator, ConfigDict

from app.utils.geo import dump_geom
from app.utils.phone import validate_phones


class OrganizationCreate(BaseModel):
    name: str
    building_id: int
    phones: list[str]
    activities: list[int]


class OrganizationUpdate(BaseModel):
    name: str | None = None
    building_id: int | None = None
    phones: list[str] | None = None
    activities: list[int] | None = None


class BuildingOutNested(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    address: str
    geolocation: Annotated[dict, BeforeValidator(dump_geom)]


class ActivityOutNested(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str


class OrganizationOutNested(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    phones: Annotated[list[str], BeforeValidator(validate_phones)]
    activities: list['ActivityOut']


class ActivityOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    children: list['ActivityOut'] = []


class BulidingOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    address: str
    geolocation: Annotated[dict, BeforeValidator(dump_geom)]
    organizations: list['OrganizationOutNested'] = []


class OrganizationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    building: 'BuildingOutNested'
    phones: Annotated[list[str], BeforeValidator(validate_phones)]
    activities: list['ActivityOutNested']


class GeolocationQuery(BaseModel):
    min_lat: float
    min_lon: float
    max_lat: float
    max_lon: float
