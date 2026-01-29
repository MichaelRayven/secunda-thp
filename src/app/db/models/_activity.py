from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.models._base import Base


class Activity(Base):
    __tablename__ = 'activities'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(), nullable=False)
    parent_id: Mapped[int] = mapped_column(
        ForeignKey('activities.id', ondelete='CASCADE'),
        nullable=True,
    )

    parent: Mapped['Activity'] = relationship('Activity', remote_side=[id], backref='children')
