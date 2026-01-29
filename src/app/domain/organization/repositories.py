from sqlalchemy import bindparam, func, select
from sqlalchemy.orm import Session

from app.common.exceptions import ModelNotFoundError
from app.db.models import (
    Activity,
    Building,
    Organization,
    OrganizationPhone,
    activity_organization_association,
)
from app.domain.organization.schemas import OrganizationCreate


class OrganizationRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_organizations_by_building(self, building: int) -> list[Organization]:
        return self.session.query(Organization).filter(Organization.building_id == building).all()

    def get_organization_by_id(self, gid: int) -> Organization | None:
        return self.session.query(Organization).get(gid)

    def get_organizations_by_name(self, name: str) -> list[Organization]:
        return self.session.query(Organization).filter(Organization.name.op('%')(name)).all()

    def get_organizations_by_activity(self, activity: int) -> list[Organization]:
        activity_children = (
            select(Activity)
            .where(Activity.id == bindparam('start_id'))
            .cte(name='activity_children', recursive=True)
        )

        recursive_part = select(Activity).join(
            activity_children,
            Activity.parent_id == activity_children.c.id,
        )

        activity_children = activity_children.union_all(recursive_part)

        query = (
            select(Organization)
            .join(activity_organization_association)
            .where(
                activity_organization_association.c.activity_id.in_(select(activity_children.c.id)),
            )
            .distinct()
        )

        result = self.session.execute(query, {'start_id': activity}).scalars().all()
        return list(result)

    def get_organizations_by_geolocation(
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
            select(Organization).join(Building).where(Building.geolocation.intersects(bounding_box))
        )
        result = self.session.execute(query).scalars().all()
        return list(result)

    def create_organization(self, organization: OrganizationCreate) -> Organization:
        # Проверяем, существование здания и активностей
        building = (
            self.session.query(Building).filter(Building.id == organization.building_id).first()
        )
        if not building:
            raise ModelNotFoundError(message='Building not found')

        activities = (
            self.session.query(Activity).filter(Activity.id.in_(organization.activities)).all()
        )
        if len(activities) != len(organization.activities):
            raise ModelNotFoundError(message='One or more activities not found')

        # Создаем организацию
        new_organization = Organization(name=organization.name)
        new_organization.building = building
        new_organization.activities = activities
        new_organization.phones = [
            OrganizationPhone(phone_number=phone) for phone in organization.phones
        ]

        self.session.add(new_organization)
        self.session.commit()
        self.session.refresh(new_organization)

        return new_organization
