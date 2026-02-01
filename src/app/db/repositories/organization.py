from typing import TYPE_CHECKING

from sqlalchemy import bindparam, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.common.exceptions import ModelNotFoundError
from app.db.models import (
    Activity as ActivityModel,
)
from app.db.models import (
    Building as BuildingModel,
)
from app.db.models import (
    Organization as OrganizationModel,
)
from app.db.models import (
    OrganizationPhone,
    activity_organization_association,
)
from app.domain.organization.entities import Activity, Building, GeoLocation, Organization
from app.domain.organization.repositories import IOrganizationRepository
from app.domain.organization.schemas import OrganizationCreate
from app.utils.geo import wkb_to_shape

if TYPE_CHECKING:
    from shapely import Point


class SQLAlchemyOrganizationRepository(IOrganizationRepository):
    TEXT_SIMILARITY = 0.2

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_organizations_by_building(self, building: int) -> list[Organization]:
        query = (
            select(OrganizationModel)
            .options(
                selectinload(OrganizationModel.building),
                selectinload(OrganizationModel.phones),
                selectinload(OrganizationModel.activities),
            )
            .where(OrganizationModel.building_id == building)
        )
        result = await self.session.execute(query)
        entities = result.scalars().all()
        return [self._to_domain(entity) for entity in entities]

    async def get_organization_by_id(self, gid: int) -> Organization:
        query = (
            select(OrganizationModel)
            .options(
                selectinload(OrganizationModel.building),
                selectinload(OrganizationModel.phones),
                selectinload(OrganizationModel.activities),
            )
            .where(OrganizationModel.id == gid)
        )
        result = await self.session.execute(query)
        model = result.scalar_one_or_none()

        if not model:
            msg = f"Organization id={gid} doesn't exist"
            raise ModelNotFoundError(msg)

        return self._to_domain(model)

    async def get_organizations_by_name(self, name: str) -> list[Organization]:
        query = select(OrganizationModel).options(
            selectinload(OrganizationModel.building),
            selectinload(OrganizationModel.phones),
            selectinload(OrganizationModel.activities),
        )

        if name and name.strip():
            query = query.where(
                func.similarity(OrganizationModel.name, name) > self.TEXT_SIMILARITY
            ).order_by(
                func.similarity(OrganizationModel.name, name).desc(),
            )

        query = query.limit(100)

        result = await self.session.execute(query)
        entities = result.scalars().all()
        return [self._to_domain(entity) for entity in entities]

    async def get_organizations_by_activity(self, activity: int) -> list[Organization]:
        activity_children = (
            select(ActivityModel)
            .where(ActivityModel.id == bindparam('start_id'))
            .cte(name='activity_children', recursive=True)
        )

        recursive_part = select(ActivityModel).join(
            activity_children,
            ActivityModel.parent_id == activity_children.c.id,
        )

        activity_children = activity_children.union_all(recursive_part)

        query = (
            select(OrganizationModel)
            .options(
                selectinload(OrganizationModel.building),
                selectinload(OrganizationModel.phones),
                selectinload(OrganizationModel.activities),
            )
            .join(activity_organization_association)
            .where(
                activity_organization_association.c.activity_id.in_(select(activity_children.c.id)),
            )
            .distinct()
        )

        result = await self.session.execute(query, {'start_id': activity})
        entities = result.scalars().all()
        return [self._to_domain(entity) for entity in entities]

    async def get_organizations_by_geolocation(
        self,
        min_lat: float,
        min_lon: float,
        max_lat: float,
        max_lon: float,
    ) -> list[Organization]:
        bounding_box = func.ST_MakeEnvelope(
            min_lon,
            min_lat,
            max_lon,
            max_lat,
            4326,
        )

        query = (
            select(OrganizationModel)
            .options(
                selectinload(OrganizationModel.building),
                selectinload(OrganizationModel.phones),
                selectinload(OrganizationModel.activities),
            )
            .join(BuildingModel)
            .where(BuildingModel.geolocation.intersects(bounding_box))
        )
        result = await self.session.execute(query)
        entities = result.scalars().all()
        return [self._to_domain(entity) for entity in entities]

    async def create_organization(self, organization: OrganizationCreate) -> Organization:
        # Проверяем существование здания
        building_query = select(BuildingModel).where(BuildingModel.id == organization.building_id)
        building_result = await self.session.execute(building_query)
        building = building_result.scalar_one_or_none()

        if not building:
            raise ModelNotFoundError(message='Building not found')

        # Проверяем существование активностей
        activities_query = select(ActivityModel).where(
            ActivityModel.id.in_(organization.activities)
        )
        activities_result = await self.session.execute(activities_query)
        activities = activities_result.scalars().all()

        if len(activities) != len(organization.activities):
            raise ModelNotFoundError(message='One or more activities not found')

        # Создаем организацию
        new_organization = OrganizationModel(name=organization.name)
        new_organization.building = building
        new_organization.activities = list(activities)
        new_organization.phones = [
            OrganizationPhone(phone_number=phone) for phone in organization.phones
        ]

        self.session.add(new_organization)
        await self.session.commit()
        await self.session.refresh(new_organization, ['building', 'phones', 'activities'])

        return self._to_domain(new_organization)

    def _to_domain(self, model: OrganizationModel) -> Organization:
        point: Point = wkb_to_shape(model.building.geolocation)  # pyright: ignore[reportAssignmentType, reportArgumentType]
        geolocation = GeoLocation(
            latitude=point.y,
            longitude=point.x,
        )
        building = Building(
            id=model.building.id,
            address=model.building.address,
            geolocation=GeoLocation(
                latitude=geolocation.latitude,
                longitude=geolocation.longitude,
            ),
        )

        phones = [phone.phone_number for phone in model.phones] if model.phones else []

        activities = (
            [Activity(id=a.id, name=a.name, parent_id=a.parent_id) for a in model.activities]
            if model.activities
            else []
        )

        return Organization(
            id=model.id,
            name=model.name,
            building_id=model.building_id,
            building=building,
            phones=phones,
            activities=activities,
        )
