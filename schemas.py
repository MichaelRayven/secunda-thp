from pydantic import BaseModel


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


class OrganizationOut(BaseModel):
    id: int
    name: str
    building: 'BulidingOut'
    phones: list[str]
    activities: list['ActivityOut']


class ActivityOut(BaseModel):
    id: int
    name: str
    children: list['ActivityOut']
    parent: 'ActivityOut' = None


class BulidingOut(BaseModel):
    id: int
    address: str
    latitude: float
    longitude: float
    organizations: list['OrganizationOut']
