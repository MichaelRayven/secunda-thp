from typing import Annotated, Any

from geoalchemy2 import WKBElement
from geoalchemy2.shape import to_shape
from pydantic import BaseModel, BeforeValidator, ConfigDict
from shapely.geometry.base import BaseGeometry


def stringify_phone(value: Any):
    if hasattr(value, 'phone_number'):
        return getattr(value, 'phone_number', None)

    if isinstance(value, str):
        return value

    raise ValueError('Please provide a valid phone number')


def validate_phones(value: Any):
    if isinstance(value, list):
        return [stringify_phone(phone) for phone in value]

    return [stringify_phone(value)]


def wkb_to_shape(wkb: WKBElement | BaseGeometry) -> BaseGeometry | None:
    if isinstance(wkb, WKBElement):
        return to_shape(wkb)

    return wkb


def dump_geom(value: Any) -> dict:
    if isinstance(value, dict):
        return value
    return getattr(wkb_to_shape(value), '__geo_interface__', None)


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
