from typing import Annotated, Any

from pydantic import BaseModel, BeforeValidator, ConfigDict


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
    latitude: float
    longitude: float


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
    latitude: float
    longitude: float
    organizations: list['OrganizationOutNested'] = []


class OrganizationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    building: 'BuildingOutNested'
    phones: Annotated[list[str], BeforeValidator(validate_phones)]
    activities: list['ActivityOutNested']
