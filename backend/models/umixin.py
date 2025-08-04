# SQLAlchemy Declarative Mixin
from sqlalchemy import Column, DateTime
from sqlalchemy.ext.declarative import declared_attr, as_declarative
from datetime import datetime, timezone


@as_declarative()
class Base:
    """
    Base class which provides automated table name
    and surrogate primary key column.
    """
    @declared_attr
    def __tablename__(cls):
        return cls.__name__.lower()


class TimestampMixin:
    created_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    deleted_at = Column(
        DateTime,
        nullable=True,
    )


# A new Base class for others to inherit from
class AppBase(Base, TimestampMixin):
    __abstract__ = True
