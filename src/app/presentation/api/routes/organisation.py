from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.common.di.services import get_organisation_service
from app.domain.organization.entities import Organization
from app.domain.organization.schemas import GeolocationQuery, OrganizationCreate, OrganizationOut
from app.domain.organization.services import OrganizationService

organization_router = APIRouter(prefix='/organizations', tags=['organizations'])


@organization_router.get('/name', response_model=list[OrganizationOut])
async def get_organization_by_name(
    q: str,
    service: Annotated[OrganizationService, Depends(get_organisation_service)],
) -> list[Organization]:
    return service.get_organizations_by_name(q)


@organization_router.get('/building', response_model=list[OrganizationOut])
async def get_organizations_by_building(
    q: int,
    service: Annotated[OrganizationService, Depends(get_organisation_service)],
) -> list[Organization]:
    return service.get_organizations_by_building(q)


@organization_router.get('/activity', response_model=list[OrganizationOut])
async def get_organizations_by_activity(
    q: int,
    service: Annotated[OrganizationService, Depends(get_organisation_service)],
) -> list[Organization]:
    return service.get_organizations_by_activity(q)


@organization_router.get('/location', response_model=list[OrganizationOut])
async def get_organizations_by_geolocation(
    query: Annotated[GeolocationQuery, Query()],
    service: Annotated[OrganizationService, Depends(get_organisation_service)],
) -> list[Organization]:
    return service.get_organizations_by_geolocation(
        min_lat=query.min_lat,
        min_lon=query.min_lon,
        max_lat=query.max_lat,
        max_lon=query.max_lon,
    )


@organization_router.post('/', response_model=OrganizationOut)
async def create_organization(
    organization: OrganizationCreate,
    service: Annotated[OrganizationService, Depends(get_organisation_service)],
) -> Organization:
    return service.create_organization(organization)


@organization_router.get('/{gid}', response_model=OrganizationOut)
async def get_organization_by_id(
    gid: int,
    service: Annotated[OrganizationService, Depends(get_organisation_service)],
) -> Organization:
    return service.get_organization_by_id(gid)
