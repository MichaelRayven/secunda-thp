from sqlalchemy.orm import Session

from app.db.db import engine
from app.domain.organization.repositories import OrganizationRepository
from app.domain.organization.services import OrganizationService


def get_session():
    with Session(engine) as session:
        yield session


def get_organisation_service(session: Session) -> OrganizationService:
    return OrganizationService(OrganizationRepository(session))
