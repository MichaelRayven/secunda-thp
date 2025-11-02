from db import SessionDep
from fastapi import APIRouter
from schemas import OrganizationCreate, OrganizationOut
from services import organizations_service

organizations_router = APIRouter(prefix='/organizations', tags=['organizations'])


@organizations_router.get('/name', response_model=list[OrganizationOut])
async def get_organization_by_name(q: str, session: SessionDep):
    return organizations_service.get_organizations_by_name(q, session)


@organizations_router.get('/building', response_model=list[OrganizationOut])
async def get_organizations_by_building(q: int, session: SessionDep):
    return organizations_service.get_organizations_by_building(q, session)


@organizations_router.get('/activity', response_model=list[OrganizationOut])
async def get_organizations_by_activity(q: int, session: SessionDep):
    return organizations_service.get_organizations_by_activity(q, session)


@organizations_router.get('/location', response_model=list[OrganizationOut])
async def get_organizations_by_geolocation(
    min_lon: float,
    min_lat: float,
    max_lon: float,
    max_lat: float,
    session: SessionDep,
):
    return organizations_service.get_organizations_by_geolocation(
        min_lat=min_lat,
        min_lon=min_lon,
        max_lat=max_lat,
        max_lon=max_lon,
        session=session,
    )


@organizations_router.post('/', response_model=OrganizationOut)
async def create_organization(organization: OrganizationCreate, session: SessionDep):
    return organizations_service.create_organization(organization, session)


@organizations_router.get('/{gid}', response_model=OrganizationOut)
async def get_organization_by_id(gid: int, session: SessionDep):
    return organizations_service.get_organization_by_id(gid, session)
