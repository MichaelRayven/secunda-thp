from db import SessionDep
from fastapi import APIRouter
from schemas import OrganizationCreate, OrganizationOut
from services import organizations_service

organizations_router = APIRouter(prefix='/organizations', tags=['organizations'])


@organizations_router.get('/{gid}', response_model=OrganizationOut)
async def get_organization_by_id(gid: int, session: SessionDep):
    return organizations_service.get_organization_by_id(gid, session)


@organizations_router.get('/', response_model=list[OrganizationOut])
async def get_organization_by_name(name: str, session: SessionDep):
    return organizations_service.get_organization_by_name(name, session)


@organizations_router.get('/building/{gid}', response_model=list[OrganizationOut])
async def get_organizations_by_building(gid: int, session: SessionDep):
    return organizations_service.get_organizations_by_building(gid, session)


@organizations_router.post('/', response_model=OrganizationOut)
async def create_organization(organization: OrganizationCreate, session: SessionDep):
    return organizations_service.create_organization(organization, session)
