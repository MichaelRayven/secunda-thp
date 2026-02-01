from typing import TYPE_CHECKING

from geoalchemy2 import Geography
from sqlalchemy import Column, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models._base import Base

if TYPE_CHECKING:
    from app.db.models._organization import Organization


class Building(Base):
    __tablename__ = 'buildings'
    id: Mapped[int] = mapped_column(primary_key=True)
    address: Mapped[str] = mapped_column(String(), nullable=False)
    geolocation = Column(Geography(geometry_type='POINT', srid=4326), nullable=False)

    organizations: Mapped[list['Organization']] = relationship(
        'Organization',
        back_populates='building',
    )
