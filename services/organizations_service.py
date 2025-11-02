from fastapi import HTTPException
from models import Activity, Building, Organization, OrganizationPhone, organization_activity
from schemas import OrganizationCreate, OrganizationOut
from sqlalchemy import bindparam, func, select
from sqlalchemy.orm import Session


def get_organizations_by_building(building: int, session: Session) -> list[OrganizationOut]:
    return session.query(Organization).filter(Organization.building_id == building).all()


def get_organization_by_id(gid: int, session: Session) -> OrganizationOut:
    organization = session.query(Organization).get(gid)
    if organization is None:
        raise HTTPException(status_code=404, detail='Organization not found')
    return organization


def get_organizations_by_name(name: str, session: Session) -> list[OrganizationOut]:
    organization = session.query(Organization).filter(Organization.name.op('%')(name)).all()
    if organization is None:
        raise HTTPException(status_code=404, detail='Organization not found')
    return organization


def get_organizations_by_activity(activity: int, session: Session) -> list[OrganizationOut]:
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
        .join(organization_activity)
        .where(
            organization_activity.c.activity_id.in_(select(activity_children.c.id)),
        )
        .distinct()
    )

    return session.execute(query, {'start_id': activity}).scalars().all()


def get_organizations_by_geolocation(
    min_lat: float,
    min_lon: float,
    max_lat: float,
    max_lon: float,
    session: Session,
) -> list[OrganizationOut]:
    bounding_box = func.ST_MakeEnvelope(
        min_lon,
        min_lat,
        max_lon,
        max_lat,
        4326,
    )

    query = select(Organization).join(Building).where(Building.geolocation.intersects(bounding_box))

    return session.execute(query).scalars().all()


def create_organization(organization: OrganizationCreate, session: Session) -> OrganizationOut:
    # Проверяем, существование здания и активностей
    building = session.query(Building).filter(Building.id == organization.building_id).first()
    if not building:
        raise HTTPException(status_code=404, detail='Building not found')

    activities = session.query(Activity).filter(Activity.id.in_(organization.activities)).all()
    if len(activities) != len(organization.activities):
        raise HTTPException(status_code=404, detail='One or more activities not found')

    # Создаем организацию
    new_organization = Organization(name=organization.name)
    new_organization.building = building
    new_organization.activities = activities
    new_organization.phones = [
        OrganizationPhone(phone_number=phone) for phone in organization.phones
    ]

    session.add(new_organization)
    session.commit()
    session.refresh(new_organization)

    return organization
