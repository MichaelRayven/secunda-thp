from app.domain.organization.entities import Organization
from app.domain.organization.repositories import IOrganizationRepository
from app.domain.organization.schemas import OrganizationCreate


class OrganizationService:
    def __init__(self, repository: IOrganizationRepository) -> None:
        self.repository = repository

    async def get_organizations_by_building(self, building: int) -> list[Organization]:
        return await self.repository.get_organizations_by_building(building)

    async def get_organization_by_id(self, gid: int) -> Organization:
        return await self.repository.get_organization_by_id(gid)

    async def get_organizations_by_name(self, name: str) -> list[Organization]:
        return await self.repository.get_organizations_by_name(name)

    async def get_organizations_by_activity(self, activity: int) -> list[Organization]:
        return await self.repository.get_organizations_by_activity(activity)

    async def get_organizations_by_geolocation(
        self,
        min_lat: float,
        min_lon: float,
        max_lat: float,
        max_lon: float,
    ) -> list[Organization]:
        return await self.repository.get_organizations_by_geolocation(min_lat, min_lon, max_lat, max_lon)

    async def create_organization(self, organization: OrganizationCreate) -> Organization:
        return await self.repository.create_organization(organization)
