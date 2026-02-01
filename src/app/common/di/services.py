from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db.db import get_session
from app.db.repositories.organization import SQLAlchemyOrganizationRepository
from app.domain.organization.repositories import IOrganizationRepository
from app.domain.organization.services import OrganizationService


def get_organization_repository(session: Annotated[Session, Depends(get_session)]):
    return SQLAlchemyOrganizationRepository(session)


def get_organisation_service(
    repo: Annotated[IOrganizationRepository, Depends(get_organization_repository)],
):
    return OrganizationService(repo)
