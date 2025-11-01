from fastapi import HTTPException
from models import Activity, Building, Organization, OrganizationPhone
from schemas import BulidingOut, OrganizationCreate, OrganizationOut
from sqlalchemy.orm import Session


def get_organizations_by_building(gid: int, session: Session) -> list[OrganizationOut]:
    return session.query(Organization).filter(Organization.building_id == gid).all()


def get_organization_by_id(gid: int, session: Session) -> OrganizationOut:
    organization = session.query(Organization).get(gid)
    if organization is None:
        raise HTTPException(status_code=404, detail='Organization not found')
    return organization


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

    return OrganizationOut(
        id=new_organization.id,
        name=new_organization.name,
        building=BulidingOut(
            id=building.id,
            address=building.address,
            latitude=building.latitude,
            longitude=building.longitude,
        ),
    )
