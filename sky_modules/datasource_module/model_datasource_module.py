from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Table
from sqlalchemy.orm import relationship, backref
from common.app_model import DataResult
from marshmallow import Schema, fields

Base = declarative_base()

# --------------------------------------------------------------------------------------------------------------------
# Many to many relationships
# --------------------------------------------------------------------------------------------------------------------
association_role_permission = Table('sky_role_pemission', Base.metadata,
                                    Column('role_id', Integer, ForeignKey('sky_role.id')),
                                    Column('permission_id', Integer, ForeignKey('sky_permission.id'))
                                    )

association_user_role = Table('sky_user_role', Base.metadata,
                              Column('user_id', Integer, ForeignKey('sky_user.id')),
                              Column('role_id', Integer, ForeignKey('sky_role.id'))
                              )


# --------------------------------------------------------------------------------------------------------------------
# Alchemy classes / Top level applications classes
# --------------------------------------------------------------------------------------------------------------------
class AlchemyUser(Base):
    __tablename__ = 'sky_user'
    id = Column(Integer, primary_key=True)
    username = Column(String(64), nullable=False)
    password = Column(String(256), nullable=False)
    first_name = Column(String(128), nullable=True)
    family_name = Column(String(128), nullable=True)
    email = Column(String(128), nullable=True)

    roles = relationship(
        "AlchemyRole",
        secondary=association_user_role)

    def __init__(self, username, password, first_name='', family_name='', email=''):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.family_name = family_name
        self.email = email

    def __repr__(self):
        return "<AlchemyUser(id= '%s', username='%s', password='%s', first_name='%s', family_name='%s', " \
               "email='%s')>" % (self.id, self.username, self.password, self.first_name, self.family_name, self.email)


class User:

    def __init__(self, user_id, username, password, first_name, family_name, email, roles):
        self.id = user_id
        self.username = username
        self.password = password
        self.first_name = first_name
        self.family_name = family_name
        self.email = email
        self.roles = roles

    def __repr__(self):
        return "<User(id= '%s', username='%s', password='%s', first_name='%s', family_name='%s', email='%s')>" % \
               (self.id, self.username, self.password, self.first_name, self.family_name, self.email)


class AlchemyRole(Base):
    __tablename__ = 'sky_role'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(String(256), nullable=True)

    permissions = relationship(
        "AlchemyPermission",
        secondary=association_role_permission)

    def __init__(self, name, description=''):
        self.name = name
        self.description = description

    def __repr__(self):
        return "<AlchemyRole(id= '%s', name='%s', description='%s')>" % (self.id, self.name, self.description)


class Role:

    def __init__(self, role_id, name, description, permissions):
        self.id = role_id
        self.name = name
        self.description = description
        self.permissions = permissions

    def __repr__(self):
        return "<Role(id= '%s', name='%s', description='%s')>" % (self.id, self.name, self.description)


class AlchemyPermission(Base):
    __tablename__ = 'sky_permission'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(String(256), nullable=True)

    def __init__(self, name, description=''):
        self.name = name
        self.description = description

    def __repr__(self):
        return "<AlchemyPermission(id= '%s', name='%s', description='%s')>" % (self.id, self.name, self.description)


class Permission:

    def __init__(self, permission_id, name, description):
        self.id = permission_id
        self.name = name
        self.description = description

    def __repr__(self):
        return "<Permission(id= '%s', name='%s', description='%s')>" % (self.id, self.name, self.description)


class AlchemyCaseType(Base):
    __tablename__ = 'sky_case_type'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(String(256), nullable=True)

    def __init__(self, name, description=''):
        self.name = name
        self.description = description

    def __repr__(self):
        return "<AlchemyCaseType(id= '%s', name='%s', description='%s')>" % (self.id, self.name, self.description)


class CaseType:

    def __init__(self, type_id, name, description=''):
        self.id = type_id
        self.name = name
        self.description = description

    def __repr__(self):
        return "<CaseType(id= '%s', name='%s', description='%s')>" % (self.id, self.name, self.description)


class AlchemyCaseStatus(Base):
    __tablename__ = 'sky_case_status'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(String(256), nullable=True)

    def __init__(self, name, description=''):
        self.name = name
        self.description = description

    def __repr__(self):
        return "<AlchemyCaseStatus(id= '%s', name='%s', description='%s')>" % (self.id, self.name, self.description)


class CaseStatus:

    def __init__(self, status_id, name, description=''):
        self.id = status_id
        self.name = name
        self.description = description

    def __repr__(self):
        return "<CaseStatus(id= '%s', name='%s', description='%s')>" % (self.id, self.name, self.description)


class AlchemyCase(Base):
    __tablename__ = 'sky_case'
    id = Column(Integer, primary_key=True)
    formal_name = Column(String(256), nullable=False)
    friend_name = Column(String(256), nullable=False)
    creation_datetime = Column(DateTime)
    num_win = Column(Integer)
    num_lin = Column(Integer)
    num_ios = Column(Integer)
    num_mal = Column(Integer)
    num_pac = Column(Integer)
    num_log = Column(Integer)

    status_id = Column(Integer, ForeignKey('sky_case_status.id'))
    status = relationship('AlchemyCaseStatus', backref=backref('sky_case'))

    type_id = Column(Integer, ForeignKey('sky_case_type.id'))
    type = relationship('AlchemyCaseType', backref=backref('sky_case'))

    def __init__(self, formal_name, friend_name, creation_datetime, num_win, num_lin, num_ios, num_mal,
                 num_pac, num_log):
        self.formal_name = formal_name
        self.friend_name = friend_name
        self.creation_datetime = creation_datetime
        self.num_win = num_win
        self.num_lin = num_lin
        self.num_ios = num_ios
        self.num_mal = num_mal
        self.num_pac = num_pac
        self.num_log = num_log

    def __repr__(self):
        return "<AlchemyCase(id= '%s', formal_name='%s', friend_name='%s', creation_datetime= '%s', num_win= '%s', " \
               "num_lin= '%s', num_ios= '%s', num_mal= '%s', num_pac= '%s', num_log)= '%s'>" % (self.id,
                                                                                                self.formal_name,
                                                                                                self.friend_name,
                                                                                                self.creation_datetime,
                                                                                                self.num_win,
                                                                                                self.num_lin,
                                                                                                self.num_ios,
                                                                                                self.num_mal,
                                                                                                self.num_pac,
                                                                                                self.num_log)


class Case:

    def __init__(self, case_id, formal_name, friend_name, creation_datetime, num_win, num_lin, num_ios, num_mal,
                 num_pac, num_log, case_type, case_status):
        self.id = case_id
        self.formal_name = formal_name
        self.friend_name = friend_name
        self.creation_datetime = creation_datetime
        self.num_win = num_win
        self.num_lin = num_lin
        self.num_ios = num_ios
        self.num_mal = num_mal
        self.num_pac = num_pac
        self.num_log = num_log
        self.case_type = case_type
        self.case_status = case_status

    def __repr__(self):
        return "<Case(id= '%s', formal_name='%s', friend_name='%s', creation_datetime= '%s', num_win= '%s', " \
               "num_lin= '%s', num_ios= '%s', num_mal= '%s', num_pac= '%s', num_log)= '%s'>" % (self.id,
                                                                                                self.formal_name,
                                                                                                self.friend_name,
                                                                                                self.creation_datetime,
                                                                                                self.num_win,
                                                                                                self.num_lin,
                                                                                                self.num_ios,
                                                                                                self.num_mal,
                                                                                                self.num_pac,
                                                                                                self.num_log)


class AlchemyEvidence(Base):
    __tablename__ = 'sky_evidence'
    id = Column(Integer, primary_key=True)
    alias = Column(String(512), nullable=False)
    size = Column(Float, nullable=False)

    owner_id = Column(Integer, ForeignKey('sky_user.id'))
    owner = relationship('AlchemyUser', backref=backref('sky_evidence'))

    def __init__(self, alias, size):
        self.alias = alias
        self.size = size

    def __repr__(self):
        return "<AlchemyEvidence(id= '%s', alias='%s', size='%s')>" % (self.id, self.alias, self.size)


class Evidence:

    def __init__(self, evidence_id, alias, size, owner):
        self.id = evidence_id
        self.alias = alias
        self.size = size
        self.owner = owner

    def __repr__(self):
        return "<Evidence(id= '%s', alias='%s', size='%s'>" % (self.id, self.alias, self.size)


class AlchemyUpload(Base):
    __tablename__ = 'sky_upload'
    id = Column(Integer, primary_key=True)
    path = Column(String(512), nullable=False)
    size = Column(Float, nullable=False)
    type = Column(String(32), nullable=False)

    evidence_id = Column(Integer, ForeignKey('sky_evidence.id'))
    evidence = relationship('AlchemyEvidence', backref=backref('sky_upload'))

    def __init__(self, path, size, type_str):
        self.path = path
        self.size = size
        self.type = type_str

    def __repr__(self):
        return "<AlchemyUpload(id= '%s', path='%s', size='%s', type='%s')>" % (self.id, self.path, self.size, self.type)


class Upload:

    def __init__(self, upload_id, path, size, type_str, evidence):
        self.id = upload_id
        self.path = path
        self.size = size
        self.type = type_str
        self.evidence = evidence

    def __repr__(self):
        return "<Upload(id= '%s', path='%s', size='%s', type='%s'>" % (self.id, self.path, self.size, self.type)


class AlchemyFile(Base):
    __tablename__ = 'sky_file'
    id = Column(Integer, primary_key=True)
    path = Column(String(512), nullable=False)
    size = Column(Float, nullable=False)
    name = Column(String(256), nullable=False)
    hash_md5 = Column(String(32), nullable=False)
    hash_sha256 = Column(String(64), nullable=False)

    upload_id = Column(Integer, ForeignKey('sky_upload.id'))
    upload = relationship('AlchemyUpload', backref=backref('sky_file'))

    def __init__(self, path, size, name, hash_md5, hash_sha256):
        self.path = path
        self.size = size
        self.name = name
        self.hash_md5 = hash_md5
        self.hash_sha256 = hash_sha256

    def __repr__(self):
        return "<AlchemyFile(id= '%s', path='%s', size='%s', name='%s', hash_md5='%s', hash_sha256='%s')>" % \
               (self.id, self.path, self.size, self.name, self.hash_md5, self.hash_sha256)


class File:

    def __init__(self, file_id, path, size, name, hash_md5, hash_sha256, upload):
        self.id = file_id
        self.path = path
        self.size = size
        self.name = name
        self.hash_md5 = hash_md5
        self.hash_sha256 = hash_sha256
        self.upload = upload

    def __repr__(self):
        return "<File(id= '%s', path='%s', size='%s', name='%s', hash_md5='%s', hash_sha256='%s')>" % \
               (self.id, self.path, self.size, self.name, self.hash_md5, self.hash_sha256)


# --------------------------------------------------------------------------------------------------------------------
# Meta clases (for general purpose)
# --------------------------------------------------------------------------------------------------------------------

class AlchemyEntity(Base):
    __tablename__ = 'sky_entity'
    id = Column(Integer, primary_key=True)
    name = Column(String(64), nullable=False)
    description = Column(String(256), nullable=True)

    def __init__(self, name, description=''):
        self.name = name
        self.description = description

    def __repr__(self):
        return "<AlchemyEntity(id= '%s', name='%s', description='%s')>" % (self.id, self.name, self.description)


class Entity:

    def __init__(self, entity_id, name, description):
        self.id = entity_id
        self.name = name
        self.description = description

    def __repr__(self):
        return "<Entity(id= '%s', name='%s', description='%s')>" % (self.id, self.name, self.description)


class AlchemyInstance(Base):
    __tablename__ = 'sky_instance'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)

    entity_id = Column(Integer, ForeignKey('sky_entity.id'))
    entity = relationship('AlchemyEntity', backref=backref('sky_instance'))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return "<AlchemyInstance(id= '%s', name='%s')>" % (self.id, self.name)


class Instance:

    def __init__(self, instance_id, name, entity):
        self.id = instance_id
        self.name = name
        self.entity = entity

    def __repr__(self):
        return "<Instance(id= '%s', name='%s'>" % (self.id, self.name)


class AlchemyProperty(Base):
    __tablename__ = 'sky_property'
    id = Column(Integer, primary_key=True)
    name = Column(String(128), nullable=False)
    description = Column(String(256), nullable=False)

    entity_id = Column(Integer, ForeignKey('sky_entity.id'))
    entity = relationship('AlchemyEntity', backref=backref('sky_property'))

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return "<AlchemyProperty(id= '%s', name='%s', description='%s')>" % (self.id, self.name, self.description)


class Property:

    def __init__(self, property_id, name, description, entity):
        self.id = property_id
        self.name = name
        self.description = description
        self.entity = entity

    def __repr__(self):
        return "<Property(id= '%s', name='%s', description='%s'>" % (self.id, self.name, self.description)


class AlchemyValue(Base):
    __tablename__ = 'sky_value'
    id = Column(Integer, primary_key=True)
    value = Column(String(256), nullable=False)

    property_id = Column(Integer, ForeignKey('sky_property.id'))
    property = relationship('AlchemyProperty', backref=backref('sky_value'))

    instance_id = Column(Integer, ForeignKey('sky_instance.id'))
    instance = relationship('AlchemyInstance', backref=backref('sky_value'))

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "<AlchemyValue(id= '%s', value='%s')>" % (self.id, self.value)


class Value:

    def __init__(self, value_id, val_property, instance, value):
        self.id = value_id
        self.property = val_property
        self.instance = instance
        self.value = value

    def __repr__(self):
        return "<Value(id= '%s', value='%s'>" % (self.id, self.value)


# --------------------------------------------------------------------------------------------------------------------
# Class to show results
# --------------------------------------------------------------------------------------------------------------------

class DatasourceResult(DataResult):

    def __init__(self, code: str, data: dict, msg: str = '', exception: Exception = None):
        DataResult.__init__(self, code, data, msg, exception)


# --------------------------------------------------------------------------------------------------------------------
# Schemas validation classes
# --------------------------------------------------------------------------------------------------------------------

class PermissionSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    description = fields.Str()


class RolesSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    description = fields.Str()
    permissions = fields.List(fields.Nested(PermissionSchema))


class UsersSchema(Schema):
    id = fields.Int()
    username = fields.Str()
    password = fields.Str()
    first_name = fields.Str()
    family_name = fields.Str()
    email = fields.Str()
    roles = fields.List(fields.Nested(RolesSchema))


class TypesSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    description = fields.Str()


class StatusSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    description = fields.Str()


class CasesSchema(Schema):
    id = fields.Int()
    formal_name = fields.Str()
    friend_name = fields.Str()
    creation_datetime = fields.DateTime()
    num_win = fields.Int()
    num_lin = fields.Int()
    num_ios = fields.Int()
    num_mal = fields.Int()
    num_pac = fields.Int()
    num_log = fields.Int()
    case_type = fields.Nested(TypesSchema)
    case_status = fields.Nested(StatusSchema)


class EvidencesSchema(Schema):
    id = fields.Int()
    alias = fields.Str()
    size = fields.Float()
    owner = fields.Nested(UsersSchema)


class UploadsSchema(Schema):
    id = fields.Int()
    path = fields.Str()
    size = fields.Float()
    type = fields.Str()
    evidence = fields.Nested(EvidencesSchema)


class FilesSchema(Schema):
    id = fields.Int()
    path = fields.Str()
    size = fields.Float()
    name = fields.Str()
    hash_md5 = fields.Str()
    hash_sha256 = fields.Str()
    upload = fields.Nested(UploadsSchema)


# --------------------------------------------------------------------------------------------------------------------
# Input validation classes
# --------------------------------------------------------------------------------------------------------------------

class RoleInputData:
    def __init__(self, name: String, description: String, permissions: None):
        self.name = name
        self.description = description
        self.permissions = permissions


class RoleInputDataSchema(Schema):
    name = fields.Str()
    description = fields.Str()
    permissions = fields.List(fields.Nested(PermissionSchema))


class UserInputData:
    def __init__(self, username: String, password: String, first_name: String, family_name: String, email: String,
                 roles: None):
        self.username = username
        self.password = password
        self.first_name = first_name
        self.family_name = family_name
        self.email = email
        self.roles = roles


class UserInputDataSchema(Schema):
    username = fields.Str()
    password = fields.Str()
    first_name = fields.Str()
    family_name = fields.Str()
    email = fields.Str()
    roles = fields.List(fields.Nested(RolesSchema))


class CaseTypeInputData:
    def __init__(self, name: String, description: String):
        self.name = name
        self.description = description


class CaseTypeInputDataSchema(Schema):
    name = fields.Str()
    description = fields.Str()


class CaseStatusInputData:
    def __init__(self, name: String, description: String):
        self.name = name
        self.description = description


class CaseStatusInputDataSchema(Schema):
    name = fields.Str()
    description = fields.Str()


class CaseInputData:
    def __init__(self, formal_name: String, friend_name: String, creation_datetime: DateTime,
                 num_win: int, num_lin: int, num_ios: int, num_mal: int, num_pac: int, num_log: int,
                 case_type: CaseTypeInputData, case_status: CaseStatusInputData):
        self.formal_name = formal_name
        self.friend_name = friend_name
        self.creation_datetime = creation_datetime
        self.num_win = num_win
        self.num_lin = num_lin
        self.num_ios = num_ios
        self.num_mal = num_mal
        self.num_pac = num_pac
        self.num_log = num_log
        self.case_type = case_type
        self.case_status = case_status


class CaseInputDataSchema(Schema):
    formal_name = fields.Str()
    friend_name = fields.Str()
    creation_datetime = fields.DateTime()
    num_win = fields.Int()
    num_lin = fields.Int()
    num_ios = fields.Int()
    num_mal = fields.Int()
    num_pac = fields.Int()
    num_log = fields.Int()
    case_type = fields.Nested(TypesSchema)
    case_status = fields.Nested(StatusSchema)


class EvidenceInputData:
    def __init__(self, alias: String, size: Float, owner: UserInputData):
        self.alias = alias
        self.size = size
        self.owner = owner


class EvidenceInputDataSchema(Schema):
    alias = fields.Str()
    size = fields.Float()
    owner = fields.Nested(UsersSchema)


class UploadInputData:
    def __init__(self, path: String, size: Float, type_str: String, evidence: EvidenceInputData):
        self.path = path
        self.size = size
        self.type = type_str
        self.evidence = evidence


class UploadInputDataSchema(Schema):
    path = fields.Str()
    size = fields.Float()
    type = fields.Str()
    evidence = fields.Nested(EvidencesSchema)


class FileInputData:

    def __init__(self, path: String, size: Float, name: String, hash_md5: String, hash_sha256: String,
                 upload: UploadInputData):
        self.path = path
        self.size = size
        self.name = name
        self.hash_md5 = hash_md5
        self.hash_sha256 = hash_sha256
        self.upload = upload


class FileInputDataSchema(Schema):
    path = fields.Str()
    size = fields.Float()
    name = fields.Str()
    hash_md5 = fields.Str()
    hash_sha256 = fields.Str()
    upload = fields.Nested(UploadsSchema)


class EntitiesSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    description = fields.Str()


class EntityInputData:

    def __init__(self, name: String, description: String):
        self.name = name
        self.description = description


class EntityInputDataSchema(Schema):
    name = fields.Str()
    description = fields.Str()


class InstancesSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    entity = fields.Nested(EntitiesSchema)


class InstanceInputData:

    def __init__(self, name: String, entity: EntityInputData):
        self.name = name
        self.entity = entity


class InstanceInputDataSchema(Schema):
    name = fields.Str()
    entity = fields.Nested(EntitiesSchema)


class PropertiesSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    description = fields.Str()
    entity = fields.Nested(EntitiesSchema)


class PropertyInputData:

    def __init__(self, name: String, description: String, entity: EntityInputData):
        self.name = name
        self.description = description
        self.entity = entity


class PropertyInputDataSchema(Schema):
    name = fields.Str()
    description = fields.Str()
    entity = fields.Nested(EntitiesSchema)


class ValuesSchema(Schema):
    id = fields.Int()
    property = fields.Nested(PropertiesSchema)
    instance = fields.Nested(InstancesSchema)
    value = fields.Str()


class ValueInputData:

    def __init__(self, val_property: PropertyInputData, instance: InstanceInputData, value: String):
        self.property = val_property
        self.instance = instance
        self.value = value


class ValueInputDataSchema(Schema):
    property = fields.Nested(PropertiesSchema)
    instance = fields.Nested(InstancesSchema)
    value = fields.Str()
