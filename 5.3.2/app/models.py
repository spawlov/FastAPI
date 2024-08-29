import os
from dotenv import find_dotenv, load_dotenv
from sqlalchemy import Text
from sqlalchemy.orm import Mapped, declarative_base, mapped_column

load_dotenv(find_dotenv())

Base = declarative_base()


class Product(Base):
    __tablename__ = "products"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[float] = mapped_column(nullable=False)
    count: Mapped[int] = mapped_column(nullable=False)
    published: Mapped[bool] = mapped_column(nullable=False, default=False)
