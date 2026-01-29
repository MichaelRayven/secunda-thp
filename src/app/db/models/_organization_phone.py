from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.models._base import Base


class OrganizationPhone(Base):
    __tablename__ = 'organization_phones'
    id: Mapped[int] = mapped_column(primary_key=True)
    organization_id: Mapped[int] = mapped_column(ForeignKey('organizations.id', ondelete='CASCADE'))
    phone_number: Mapped[str] = mapped_column(String(), nullable=False)
