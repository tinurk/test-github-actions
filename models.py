from typing import Optional

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from database import Base


class Recipe(Base):
    __tablename__ = "recipes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String)
    views: Mapped[int] = mapped_column(Integer, default=0)
    cooking_time: Mapped[int] = mapped_column(Integer)
    ingredients: Mapped[str] = mapped_column(String)
    description: Mapped[Optional[str]] = mapped_column(String)
