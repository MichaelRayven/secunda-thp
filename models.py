from sqlalchemy import Column, Float, ForeignKey, Integer, String, Table
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class Activity(Base):
    __tablename__ = 'activities'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(), nullable=False)
    parent_id: Mapped[int] = mapped_column(
        ForeignKey('activities.id', ondelete='CASCADE'),
        nullable=True,
    )

    parent: Mapped['Activity'] = relationship('Activity', remote_side=[id], backref='children')


# Модель здания
class Building(Base):
    __tablename__ = 'buildings'
    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(String(), nullable=False)
    latitude: Mapped[float] = mapped_column(Float(), nullable=False)
    longitude: Mapped[float] = mapped_column(Float(), nullable=False)

    organizations: Mapped[list['Organization']] = relationship(
        'Organization',
        back_populates='building',
    )


# Ассоциация "организация-виды деятельности"
organization_activity = Table(
    'organization_activity',
    Base.metadata,
    Column('organization_id', Integer, ForeignKey('organizations.id'), primary_key=True),
    Column('activity_id', Integer, ForeignKey('activities.id'), primary_key=True),
)


# Ассоциация "организация-телефоны"
class OrganizationPhone(Base):
    __tablename__ = 'organization_phones'
    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey('organizations.id', ondelete='CASCADE'))
    phone_number: Mapped[str] = mapped_column(String(), nullable=False)


# Модель организации
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
        secondary=organization_activity,
        backref='organizations',
    )
