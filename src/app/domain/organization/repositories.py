from abc import ABC, abstractmethod

from sqlalchemy.orm import Session

from app.domain.organization.entities import Organization
from app.domain.organization.schemas import OrganizationCreate


class IOrganizationRepository(ABC):
    def __init__(self, session: Session) -> None:
        self.session = session

    @abstractmethod
    def get_organizations_by_building(self, building: int) -> list[Organization]:
        raise NotImplementedError

    @abstractmethod
    def get_organization_by_id(self, gid: int) -> Organization:
        raise NotImplementedError

    @abstractmethod
    def get_organizations_by_name(self, name: str) -> list[Organization]:
        raise NotImplementedError

    @abstractmethod
    def get_organizations_by_activity(self, activity: int) -> list[Organization]:
        raise NotImplementedError

    @abstractmethod
    def get_organizations_by_geolocation(
        self,
        min_lat: float,
        min_lon: float,
        max_lat: float,
        max_lon: float,
    ) -> list[Organization]:
        raise NotImplementedError

    @abstractmethod
    def create_organization(self, organization: OrganizationCreate) -> Organization:
        raise NotImplementedError
