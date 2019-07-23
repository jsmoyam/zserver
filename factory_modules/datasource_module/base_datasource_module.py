import datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Table, Boolean

from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# Some default values
default_creation_datetime = datetime.datetime.utcnow
collation = "utf8mb4_unicode_ci"

Base = declarative_base()
metadata = Base.metadata


t_user_permission = Table(
    'user_permission', metadata,
    Column('user_id', ForeignKey('user.id'), primary_key=True, nullable=False, index=True),
    Column('permission_id', ForeignKey('permission.id'), primary_key=True, nullable=False, index=True)
)

t_user_role_permission = Table(
    'user_role_permission', metadata,
    Column('user_role_id', ForeignKey('user_role.id'), primary_key=True, nullable=False, index=True),
    Column('permission_id', ForeignKey('permission.id'), primary_key=True, nullable=False, index=True)
)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(255, collation), nullable=False, unique=True)
    password = Column(String(64, collation), nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)
    creation_date = Column(DateTime, nullable=False, default=default_creation_datetime)

    permissions = relationship('Permission', secondary=t_user_permission)


class UserRole(Base):
    __tablename__ = 'user_role'

    id = Column(Integer, primary_key=True)
    name = Column(String(31, collation), nullable=False)

    permissions = relationship('Permission', secondary=t_user_role_permission)


class Permission(Base):
    __tablename__ = 'permission'

    id = Column(Integer, primary_key=True)
    name = Column(String(63, 'utf8mb4_unicode_ci'), nullable=False)

    users = relationship('User', secondary=t_user_permission)
    user_roles = relationship('UserRole', secondary=t_user_role_permission)
