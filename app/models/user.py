from datetime import date
from typing import Optional

from sqlalchemy import Date, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    designation: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    dob: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    status: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

