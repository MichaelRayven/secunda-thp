from typing import TYPE_CHECKING

from sqlalchemy import Column, ForeignKey, String, Table
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models._base import Base

if TYPE_CHECKING:
    from app.db.models._activity import Activity
    from app.db.models._building import Building
    from app.db.models._organization_phone import OrganizationPhone

activity_organization_association = Table(
    'organization_activity',
    Base.metadata,
    Column('organization_id', ForeignKey('organization.id'), primary_key=True),
    Column('activity_id', ForeignKey('activity.id'), primary_key=True),
)


class Organization(Base):
    __tablename__ = 'organizations'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(), nullable=False)
    building_id: Mapped[int] = mapped_column(
        ForeignKey('buildings.id', ondelete='CASCADE'),
        nullable=False,
    )

    building: Mapped['Building'] = relationship('Building', back_populates='organizations')
    phones: Mapped[list['OrganizationPhone']] = relationship(
        'OrganizationPhone',
        cascade='all, delete-orphan',
    )
    activities: Mapped[list['Activity']] = relationship(
        'Activity',
        secondary=activity_organization_association,
        backref='organizations',
    )
