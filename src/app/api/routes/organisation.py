from typing import Annotated
from common.di.services import get_organization_service
from fastapi import APIRouter, Depends, Query
from domain.organization.schemas import GeolocationQuery, OrganizationCreate, OrganizationOut
from domain.organization.services import OrganisationService

organizations_router = APIRouter(prefix='/organizations', tags=['organizations'])


@organizations_router.get('/name')
async def get_organization_by_name(q: str, service: OrganisationService = Depends(get_organisation_service)) -> list[OrganizationOut]:
    return service.get_organizations_by_name(q)


@organizations_router.get('/building')
async def get_organizations_by_building(q: int, service: OrganisationService = Depends(get_organisation_service)) -> list[OrganizationOut]:
    return service.get_organizations_by_building(q)


@organizations_router.get('/activity')
async def get_organizations_by_activity(q: int, service: OrganisationService = Depends(get_organisation_service)) -> list[OrganizationOut]:
    return service.get_organizations_by_activity(q)


@organizations_router.get('/location')
async def get_organizations_by_geolocation(
    query: Annotated[GeolocationQuery, Query()],
    service: OrganisationService = Depends(get_organisation_service)
) -> list[OrganizationOut]:
    return service.get_organizations_by_geolocation(
        min_lat=min_lat,
        min_lon=min_lon,
        max_lat=max_lat,
        max_lon=max_lon
    )


@organizations_router.post('/')
async def create_organization(organization: OrganizationCreate, service: OrganisationService = Depends(get_organisation_service)) -> OrganizationOut:
    return service.create_organization(organization)


@organizations_router.get('/{gid}')
async def get_organization_by_id(gid: int, service: OrganisationService = Depends(get_organisation_service)) -> OrganizationOut:
    return service.get_organization_by_id(gid)
