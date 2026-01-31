from app.domain.organization.entities import Organization
from app.domain.organization.repositories import IOrganizationRepository
from app.domain.organization.schemas import OrganizationCreate


class OrganizationService:
    def __init__(self, repository: IOrganizationRepository) -> None:
        self.repository = repository

    def get_organizations_by_building(self, building: int) -> list[Organization]:
        return self.repository.get_organizations_by_building(building)

    def get_organization_by_id(self, gid: int) -> Organization:
        return self.repository.get_organization_by_id(gid)

    def get_organizations_by_name(self, name: str) -> list[Organization]:
        return self.repository.get_organizations_by_name(name)

    def get_organizations_by_activity(self, activity: int) -> list[Organization]:
        return self.repository.get_organizations_by_activity(activity)

    def get_organizations_by_geolocation(
        self,
        min_lat: float,
        min_lon: float,
        max_lat: float,
        max_lon: float,
    ) -> list[Organization]:
        return self.repository.get_organizations_by_geolocation(min_lat, min_lon, max_lat, max_lon)

    def create_organization(self, organization: OrganizationCreate) -> Organization:
        return self.repository.create_organization(organization)
