from common import config

from sky_modules.sky_module import SkyModule
from sky_modules.datasource_module import MODULE_NAME, ENGINE_NAME
from sky_modules.datasource_module.views_datasource_module import DatasourceModuleView, CreateRoleModuleView, \
    CreateUserModuleView, CreateCaseTypeModuleView, CreateCaseStatusModuleView, CreateCaseModuleView, \
    CreateEvidenceModuleView, CreateUploadModuleView, CreateFileModuleView, CreateEntityModuleView, \
    CreateInstanceModuleView, CreatePropertyModuleView, CreateValueModuleView
from sky_modules.datasource_module.model_datasource_module import Base, Permission, AlchemyPermission, \
    AlchemyRole, Role, AlchemyUser, User, AlchemyCaseType, CaseType, AlchemyCaseStatus, CaseStatus, \
    AlchemyCase, Case, AlchemyEvidence, Evidence, AlchemyUpload, Upload, AlchemyFile, File, AlchemyEntity, Entity, \
    AlchemyInstance, Instance, AlchemyProperty, Property, AlchemyValue, Value
from sky_modules.datasource_module.shells_datasource_module import DatasourceModuleShell
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from common.app_model import AppException, GenericErrorMessages

logger = config.get_log(MODULE_NAME)


class DatasourceModule(SkyModule):

    def initialize(self):
        """
        This method create and initialize all variables and resources that are needed
        :return: None
        """

        try:
            self.engine = create_engine(ENGINE_NAME)

            Session = sessionmaker(bind=self.engine)
            self.session = Session()
            Base.metadata.create_all(self.engine)

            self.register_url(DatasourceModuleView, '/ds')
            self.register_url(CreateRoleModuleView, '/ds/createrole')
            self.register_url(CreateUserModuleView, '/ds/createuser')
            self.register_url(CreateCaseTypeModuleView, '/ds/createcasetype')
            self.register_url(CreateCaseStatusModuleView, '/ds/createcasestatus')
            self.register_url(CreateCaseModuleView, '/ds/createcase')
            self.register_url(CreateEvidenceModuleView, '/ds/createevidence')
            self.register_url(CreateUploadModuleView, '/ds/createupload')
            self.register_url(CreateFileModuleView, '/ds/createfile')
            self.register_url(CreateEntityModuleView, '/ds/createentity')
            self.register_url(CreateInstanceModuleView, '/ds/createinstance')
            self.register_url(CreatePropertyModuleView, '/ds/createproperty')
            self.register_url(CreateValueModuleView, '/ds/createvalue')

            '''
            # AMJ: TEMP
            # Create permissions
            self.create_permission('p1', 'init_pppp1')
            self.create_permission('p2', 'init_pppp2')
            self.create_permission('p3', 'init_pppp3')

            permission_list = list()
            per = self.get_permission(1)
            permission_list.append(per)
            per2 = self.get_permission(2)
            permission_list.append(per2)

            # Create roles
            self.create_role('init_name', 'init_des', permission_list)
            permission_list = list()
            per3 = self.get_permission(3)
            permission_list.append(per2)
            permission_list.append(per3)
            self.create_role('role2', 'desc_role 2', permission_list)

            # Create users
            roles_list = list()
            r1 = self.get_role(1)
            r2 = self.get_role(2)
            roles_list.append(r1)
            self.create_user('ini_user', 'ini_passwd', 'ini_first', 'ini_fam', 'ini_email', roles_list)
            roles_list.append(r2)
            self.create_user('ini_user2', 'ini_passwd2', 'ini_first2', 'ini_fam2', 'ini_email2', roles_list)

            # Create case types
            self.create_case_type('ctype 1', 'case descrp 1')
            self.create_case_type('ctype 2', 'case descrp 2')
            self.create_case_type('ctype 3', 'case descrp 3')

            # Create case status
            self.create_case_status('cstatus 1', 'status descrp 1')
            self.create_case_status('cstatus 2', 'status descrp 2')
            self.create_case_status('cstatus 3', 'status descrp 3')

            # Create case
            case_type = self.get_case_type(2)
            case_status = self.get_case_status(1)
            self.create_case('formal1', 'friend1', datetime.datetime.now(), 1, 2, 3, 4, 5, 6, case_type, case_status)

            case_type = self.get_case_type(3)
            case_status = self.get_case_status(2)
            self.create_case('formal2', 'friend2', datetime.datetime.now(), 7, 8, 9, 10, 11, 12, case_type, case_status)

            # Create evidence
            owner1 = self.get_user(1)
            owner2 = self.get_user(2)
            self.create_evidence('alias 1', 11.1, owner1)
            self.create_evidence('alias 2', 22.2, owner2)

            # Create upload
            evidence1 = self.get_evidence(1)
            evidence2 = self.get_evidence(2)

            self.create_upload('path 11', 123.1, 'type 11', evidence1)
            self.create_upload('path 12', 256.32, 'type 12', evidence1)

            self.create_upload('path 21', 0.65, 'type 21', evidence2)
            self.create_upload('path 22', 512.2, 'type 22', evidence2)
            self.create_upload('path 23', 1.45, 'type 23', evidence2)
            self.create_upload('path 24', 1024.65, 'type 24', evidence2)

            # Create file
            upload1 = self.get_upload(1)
            upload2 = self.get_upload(2)

            self.create_file('file path 11', 1.11, 'file name 11', 'file has 5 11', 'file has256 11', upload1)
            self.create_file('file path 12', 2.22, 'file name 12', 'file has 5 12', 'file has256 12', upload1)

            self.create_file('file path 21', 101.11, 'file name 21', 'file has 5 21', 'file has256 21', upload2)
            self.create_file('file path 22', 102.22, 'file name 22', 'file has 5 22', 'file has256 22', upload2)
            self.create_file('file path 23', 103.33, 'file name 23', 'file has 5 23', 'file has256 23', upload2)

            #Create entity
            entity1 = self.create_entity('ent name 1', 'ent desc 1')
            entity2 = self.create_entity('ent name 2', 'ent desc 2')

            #Create instances
            instance1 = self.create_instance("instance 11", entity1[0])
            instance2 = self.create_instance("instance 12", entity1[0])
            instance3 = self.create_instance("instance 13", entity1[0])

            self.create_instance("instance 21", entity2[0])
            self.create_instance("instance 22", entity2[0])

            #Create properties
            property11 = self.create_property('pro name 11', 'pro desc 11', entity1[0])
            property12 = self.create_property('pro name 12', 'pro desc 12', entity1[0])
            property13 = self.create_property('pro name 13', 'pro desc 13', entity1[0])

            property21 = self.create_property('pro name 21', 'pro desc 21', entity2[0])
            property22 = self.create_property('pro name 22', 'pro desc 22', entity2[0])
            property23 = self.create_property('pro name 23', 'pro desc 23', entity2[0])
            property24 = self.create_property('pro name 24', 'pro desc 24', entity2[0])

            #Create values
            self.create_value(property11[0], instance1[0], 'value 11')
            self.create_value(property12[0], instance1[0], 'value 12')
            self.create_value(property13[0], instance1[0], 'value 13')

            self.create_value(property21[0], instance2[0], 'value 21')
            self.create_value(property22[0], instance2[0], 'value 22')
            self.create_value(property23[0], instance2[0], 'value 23')
            self.create_value(property24[0], instance2[0], 'value 24')

            #Check user in db
            user_id_si = self.get_user_id('ini_user', 'ini_passwd')
            user_id_no = self.get_user_id('aaaaaaa', 'bbbb')
            '''

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def get_all_permissions(self):
        """
        This method retrieves all permissions from DB
        :return: {Permission}
        """

        try:
            alchemy_permission_list = self.session.query(AlchemyPermission).all()

            permission_list = list()

            for perm in alchemy_permission_list:
                new_permission = Permission(perm.id, perm.name, perm.description)
                permission_list.append(new_permission)

            return permission_list

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def get_permission(self, permission_id):
        """
        This method retrieves permission with given id from DB
        :return: {Permission}
        """
        try:
            alchemy_permission = self.session.query(AlchemyPermission).filter_by(id=permission_id).first()

            if alchemy_permission is None:
                new_permission = None
            else:
                new_permission = Permission(alchemy_permission.id, alchemy_permission.name,
                                            alchemy_permission.description)

            return new_permission

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def alchemy_get_permission(self, permission_id):
        """
        This method retrieves an alchemy permission with given id from DB
        Not included in views (not published)
        :return: {AlchemyPermission}
        """
        try:
            alchemy_permission = self.session.query(AlchemyPermission).filter_by(id=permission_id).first()

            return alchemy_permission

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def create_permission(self, name, description):
        """
        This method inserts a new alchemy permission in DB
        :return: {Permission, Boolean}
        """
        try:
            alchemy_permission = AlchemyPermission(name, description)

            self.session.add(alchemy_permission)

            self.session.commit()

            permission = Permission(alchemy_permission.id, alchemy_permission.name, alchemy_permission.description)

            return permission, True

        except Exception:
            return None, False

    def get_all_roles(self):
        """
        This method retrieves all roles from DB
        :return: {Role}
        """
        try:
            alchemy_roles_list = self.session.query(AlchemyRole).all()

            role_list = list()

            for r in alchemy_roles_list:
                perm_list = list()
                for p in r.permissions:
                    perm = Permission(p.id, p.name, p.description)
                    perm_list.append(perm)
                new_role = Role(r.id, r.name, r.description, perm_list)
                role_list.append(new_role)

            return role_list

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def get_role(self, role_id):
        """
        This method retrieves roles with given id from DB
        :return: Role
        """
        try:
            alchemy_role = self.session.query(AlchemyRole).filter_by(id=role_id).first()

            if alchemy_role is None:
                new_role = None
            else:
                permissions_list = list()
                for p in alchemy_role.permissions:
                    perm = Permission(p.id, p.name, p.description)
                    permissions_list.append(perm)
                new_role = Role(alchemy_role.id, alchemy_role.name, alchemy_role.description, permissions_list)

            return new_role

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def alchemy_get_role(self, role_id):
        """
        This method retrieves an alchemy role with given id from DB
        Not included in views (not published)
        :return: {AlchemyRole}
        """
        try:
            alchemy_role = self.session.query(AlchemyRole).filter_by(id=role_id).first()

            return alchemy_role

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def create_role(self, name, description, permissions):
        """
        This method inserts a new alchemy role in DB
        :return: Role, Boolean
        """
        try:
            alchemy_role = AlchemyRole(name, description)

            alchemy_permission_list = list()

            for p in permissions:
                alchemy_perm = self.alchemy_get_permission(p.id)
                alchemy_permission_list.append(alchemy_perm)

            alchemy_role.permissions = alchemy_permission_list

            self.session.add(alchemy_role)

            self.session.commit()

            role = Role(alchemy_role.id, alchemy_role.name, alchemy_role.description, permissions)

            return role, True

        except Exception:
            return None, False

    def get_all_users(self):
        """
        This method retrieves all users from DB
        :return: {User}
        """
        try:
            alchemy_users_list = self.session.query(AlchemyUser).all()

            user_list = list()

            for u in alchemy_users_list:
                role_list = list()
                for r in u.roles:
                    permission_list = list()
                    for p in r.permissions:
                        new_permission = Permission(p.id, p.name, p.description)
                        permission_list.append(new_permission)
                    role = Role(r.id, r.name, r.description, permission_list)
                    role_list.append(role)
                new_user = User(u.id, u.username, u.password, u.first_name, u.family_name, u.email, role_list)
                user_list.append(new_user)

            return user_list

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def get_user(self, user_id):
        """
        This method retrieves users with given id from DB
        :return: User
        """
        try:
            alchemy_user = self.session.query(AlchemyUser).filter_by(id=user_id).first()

            if alchemy_user is None:
                new_user = None
            else:
                role_list = list()
                for r in alchemy_user.roles:
                    permissions_list = list()
                    for p in r.permissions:
                        new_permission = Permission(p.id, p.name, p.description)
                        permissions_list.append(new_permission)
                    new_role = Role(r.id, r.name, r.description, permissions_list)
                    role_list.append(new_role)

                new_user = User(alchemy_user.id, alchemy_user.username, alchemy_user.password, alchemy_user.first_name,
                                alchemy_user.family_name, alchemy_user.email, role_list)

            return new_user

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def get_user_id(self, name, password):
        """
        This method retrieves user with given name and password (None if it doesn't exist)
        :return: Int
        """
        try:
            alchemy_user = self.session.query(AlchemyUser).filter_by(username=name, password=password).first()
            if alchemy_user:
                return alchemy_user.id
            else:
                return None

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def create_user(self, username, password, first_name, family_name, email, roles):
        """
        This method inserts a new alchemy user in DB
        :return: User, Boolean
        """
        try:
            alchemy_user = AlchemyUser(username, password, first_name, family_name, email)

            alchemy_roles_list = list()

            for r in roles:
                alchemy_role = self.alchemy_get_role(r.id)
                alchemy_roles_list.append(alchemy_role)

            alchemy_user.roles = alchemy_roles_list

            self.session.add(alchemy_user)

            self.session.commit()

            user = User(alchemy_user.id, alchemy_user.username, alchemy_user.password, alchemy_user.first_name,
                        alchemy_user.family_name, alchemy_user.email, roles)

            return user, True

        except Exception:
            return None, False

    def get_all_case_types(self):
        """
        This method retrieves all case types from DB
        :return: {CaseType}
        """
        try:
            alchemy_case_types_list = self.session.query(AlchemyCaseType).all()
            case_types_list = list()

            for t in alchemy_case_types_list:
                new_type = CaseType(t.id, t.name, t.description)
                case_types_list.append(new_type)

            return case_types_list

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def get_case_type(self, type_id):
        """
        This method retrieves case type with given id from DB
        :return: CaseType
        """
        try:
            alchemy_case_type = self.session.query(AlchemyCaseType).filter_by(id=type_id).first()

            if alchemy_case_type is None:
                new_case_type = None
            else:
                new_case_type = CaseType(alchemy_case_type.id, alchemy_case_type.name, alchemy_case_type.description)

            return new_case_type

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def alchemy_get_case_type(self, type_id):
        """
        This method retrieves case status with given id from DB
        :return: AlchemyCaseType
        """
        try:
            alchemy_case_type = self.session.query(AlchemyCaseType).filter_by(id=type_id).first()

            return alchemy_case_type

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def create_case_type(self, name, description):
        """
        This method inserts a new alchemy case type in DB
        :return: CaseType, Boolean
        """
        try:
            alchemy_type = AlchemyCaseType(name, description)
            self.session.add(alchemy_type)
            self.session.commit()

            new_type = CaseType(alchemy_type.id, alchemy_type.name, alchemy_type.description)

            return new_type, True

        except Exception:
            return None, False

    def get_all_case_status(self):
        """
        This method retrieves all case status from DB
        :return: {CaseStatus}
        """
        try:
            alchemy_case_status_list = self.session.query(AlchemyCaseStatus).all()

            case_status_list = list()

            for s in alchemy_case_status_list:
                new_status = CaseStatus(s.id, s.name, s.description)
                case_status_list.append(new_status)

            return case_status_list

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def get_case_status(self, status_id):
        """
        This method retrieves case status with given id from DB
        :return: CaseStatus
        """
        try:
            alchemy_case_status = self.session.query(AlchemyCaseStatus).filter_by(id=status_id).first()

            if alchemy_case_status is None:
                new_case_status = None
            else:
                new_case_status = CaseStatus(alchemy_case_status.id, alchemy_case_status.name,
                                             alchemy_case_status.description)

            return new_case_status

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def alchemy_get_case_status(self, status_id):
        """
        This method retrieves case status with given id from DB
        :return: AlchemyCaseStatus
        """
        try:
            alchemy_case_status = self.session.query(AlchemyCaseStatus).filter_by(id=status_id).first()

            return alchemy_case_status

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def create_case_status(self, name, description):
        """
        This method inserts a new alchemy case status in DB
        :return: CaseStatus, Boolean
        """
        try:
            alchemy_status = AlchemyCaseStatus(name, description)
            self.session.add(alchemy_status)
            self.session.commit()

            new_status = CaseStatus(alchemy_status.id, alchemy_status.name, alchemy_status.description)

            return new_status, True

        except Exception:
            return None, False

    def get_all_cases(self):
        """
        This method retrieves all cases from DB
        :return: {Case}
        """
        try:
            alchemy_cases_list = self.session.query(AlchemyCase).all()

            case_list = list()

            for c in alchemy_cases_list:
                case_type = CaseType(c.type.id, c.type.name, c.type.description)
                case_status = CaseStatus(c.status.id, c.status.name, c.status.description)
                new_case = Case(c.id, c.formal_name, c.friend_name, c.creation_datetime, c.num_win, c.num_lin,
                                c.num_ios, c.num_mal, c.num_pac, c.num_log, case_type, case_status)
                case_list.append(new_case)

            return case_list

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def get_case(self, case_id):
        """
        This method retrieves cases with given id from DB
        :return: Case
        """
        try:
            alchemy_case = self.session.query(AlchemyCase).filter_by(id=case_id).first()

            if alchemy_case is None:
                new_case = None
            else:
                new_type = CaseType(alchemy_case.type.id, alchemy_case.type.name, alchemy_case.type.description)
                status = CaseStatus(alchemy_case.status.id, alchemy_case.status.name, alchemy_case.status.description)
                new_case = Case(alchemy_case.id, alchemy_case.formal_name, alchemy_case.friend_name,
                                alchemy_case.creation_datetime, alchemy_case.num_win, alchemy_case.num_lin,
                                alchemy_case.num_ios, alchemy_case.num_mal, alchemy_case.num_pac, alchemy_case.num_log,
                                new_type, status)

            return new_case

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def create_case(self, formal_name, friend_name, creation_datetime, num_win, num_lin, num_ios,
                    num_mal, num_pac, num_log, case_type, case_status):
        """
        This method inserts a new alchemy case in DB
        :return: Case, Boolean
        """
        try:
            alchemy_case_type = self.alchemy_get_case_type(case_type.id)
            alchemy_case_status = self.alchemy_get_case_status(case_status.id)

            alchemy_case = AlchemyCase(formal_name, friend_name, creation_datetime, num_win, num_lin, num_ios,
                                       num_mal, num_pac, num_log)

            alchemy_case.type = alchemy_case_type
            alchemy_case.status = alchemy_case_status

            self.session.add(alchemy_case)
            self.session.commit()

            new_type = CaseStatus(alchemy_case_type.id, alchemy_case_type.name, alchemy_case_type.description)
            status = CaseStatus(alchemy_case_status.id, alchemy_case_status.name, alchemy_case_status.description)
            case = Case(alchemy_case.id, alchemy_case.formal_name, alchemy_case.friend_name,
                        alchemy_case.creation_datetime, alchemy_case.num_win, alchemy_case.num_lin,
                        alchemy_case.num_ios, alchemy_case.num_mal, alchemy_case.num_pac, alchemy_case.num_log,
                        new_type, status)

            return case, True

        except Exception:
            return None, False

    def get_all_evidences(self):
        """
        This method retrieves all evidences from DB
        :return: {Evidence}
        """
        try:
            alchemy_evidences_list = self.session.query(AlchemyEvidence).all()
            evidence_list = list()

            for e in alchemy_evidences_list:
                roles_list = list()
                for r in e.owner.roles:
                    permission_list = list()
                    for p in r.permissions:
                        new_permission = Permission(p.id, p.name, p.description)
                        permission_list.append(new_permission)
                    new_role = Role(r.id, r.name, r.description, permission_list)
                    roles_list.append(new_role)

                new_user = User(e.owner.id, e.owner.username, e.owner.password, e.owner.first_name, e.owner.family_name,
                                e.owner.email, roles_list)
                new_evidence = Evidence(e.id, e.alias, e.size, new_user)
                evidence_list.append(new_evidence)

            return evidence_list

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def get_evidence(self, evidence_id):
        """
        This method retrieves evidences with given id from DB
        :return: Evidence
        """
        try:
            alchemy_evidence = self.session.query(AlchemyEvidence).filter_by(id=evidence_id).first()

            if alchemy_evidence is None:
                new_evidence = None
            else:
                roles_list = list()
                for r in alchemy_evidence.owner.roles:
                    permissions_list = list()
                    for p in r.permissions:
                        new_permission = Permission(p.id, p.name, p.description)
                        permissions_list.append(new_permission)
                    new_role = Role(evidence_id, r.name, r.description, permissions_list)
                    roles_list.append(new_role)
                new_user = User(alchemy_evidence.owner.id, alchemy_evidence.owner.username,
                                alchemy_evidence.owner.password,
                                alchemy_evidence.owner.first_name, alchemy_evidence.owner.family_name,
                                alchemy_evidence.owner.email, roles_list)
                new_evidence = Evidence(alchemy_evidence.id, alchemy_evidence.alias, alchemy_evidence.size, new_user)

            return new_evidence

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def alchemy_get_user(self, user_id):
        """
        This method retrieves an alchemy user with given id from DB
        Not included in views (not published)
        :return: {AlchemyUser}
        """
        try:
            alchemy_user = self.session.query(AlchemyUser).filter_by(id=user_id).first()

            return alchemy_user

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def create_evidence(self, alias, size, owner):
        """
        This method inserts a new alchemy evidence in DB
        :return: Evidence, Boolean
        """
        try:
            alchemy_owner = self.alchemy_get_user(owner.id)

            alchemy_evidence = AlchemyEvidence(alias, size)
            alchemy_evidence.owner = alchemy_owner

            self.session.add(alchemy_evidence)
            self.session.commit()

            evidence = Evidence(alchemy_evidence.id, alchemy_evidence.alias, alchemy_evidence.size, owner)

            return evidence, True

        except Exception:
            return None, False

    def alchemy_get_evidence(self, evidence_id):
        """
        This method retrieves an alchemy evidence with given id from DB
        Not included in views (not published)
        :return: {AlchemyEvidence}
        """

        try:
            alchemy_evidence = self.session.query(AlchemyEvidence).filter_by(id=evidence_id).first()

            return alchemy_evidence

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def get_all_uploads(self, evidence_id):
        """
        This method retrieves all uploads from DB that belongs to evidence_id
        :return: {Upload}
        """
        try:
            alchemy_upload_list = self.session.query(AlchemyUpload).filter_by(evidence_id=evidence_id).all()

            upload_list = list()

            for u in alchemy_upload_list:
                roles_list = list()
                for r in u.evidence.owner.roles:
                    permission_list = list()
                    for p in r.permissions:
                        new_permission = Permission(p.id, p.name, p.description)
                        permission_list.append(new_permission)
                    new_role = Role(r.id, r.name, r.description, permission_list)
                    roles_list.append(new_role)
                new_user = User(u.evidence.owner.id, u.evidence.owner.username, u.evidence.owner.password,
                                u.evidence.owner.first_name, u.evidence.owner.family_name, u.evidence.owner.email,
                                roles_list)
                new_evidence = Evidence(u.evidence.id, u.evidence.alias, u.evidence.size, new_user)
                new_upload = Upload(u.id, u.path, u.size, u.type, new_evidence)
                upload_list.append(new_upload)

            return upload_list

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def get_upload(self, upload_id):
        """
        This method retrieves uploads with given id from DB
        :return: Upload
        """
        try:
            alchemy_upload = self.session.query(AlchemyUpload).filter_by(id=upload_id).first()
            if alchemy_upload is None:
                new_upload = None
            else:

                roles_list = list()
                for r in alchemy_upload.evidence.owner.roles:
                    permissions_list = list()
                    for p in r.permissions:
                        new_permission = Permission(p.id, p.name, p.description)
                        permissions_list.append(new_permission)
                    new_role = Role(r.id, r.name, r.description, permissions_list)
                    roles_list.append(new_role)

                new_user = User(alchemy_upload.evidence.owner.id, alchemy_upload.evidence.owner.username,
                                alchemy_upload.evidence.owner.password, alchemy_upload.evidence.owner.first_name,
                                alchemy_upload.evidence.owner.family_name, alchemy_upload.evidence.owner.email,
                                roles_list)
                new_evidence = Evidence(alchemy_upload.evidence.id, alchemy_upload.evidence.alias,
                                        alchemy_upload.evidence.size, new_user)
                new_upload = Upload(alchemy_upload.id, alchemy_upload.path, alchemy_upload.size, alchemy_upload.type,
                                    new_evidence)

            return new_upload

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def create_upload(self, path, size, type_str, evidence):
        """
        This method inserts a new alchemy upload in DB
        :return: Upload, Boolean
        """
        try:
            alchemy_evidence = self.alchemy_get_evidence(evidence.id)
            alchemy_upload = AlchemyUpload(path, size, type_str)
            alchemy_upload.evidence = alchemy_evidence

            self.session.add(alchemy_upload)
            self.session.commit()

            upload = Upload(alchemy_upload.id, alchemy_upload.path, alchemy_upload.size, alchemy_upload.type, evidence)

            return upload, True

        except Exception:
            return None, False

    def alchemy_get_upload(self, upload_id):
        """
        This method retrieves an alchemy upload with given id from DB
        Not included in views (not published)
        :return: {AlchemyUpload}
        """
        try:
            alchemy_upload = self.session.query(AlchemyUpload).filter_by(id=upload_id).first()

            return alchemy_upload

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def get_all_files(self, upload_id):
        """
        This method retrieves all files from DB that belongs to upload_id
        :return: {File}
        """
        try:
            alchemy_file_list = self.session.query(AlchemyFile).filter_by(upload_id=upload_id).all()
            file_list = list()

            for f in alchemy_file_list:
                roles_list = list()
                for r in f.upload.evidence.owner.roles:
                    permission_list = list()
                    for p in r.permissions:
                        new_permission = Permission(p.id, p.name, p.description)
                        permission_list.append(new_permission)
                    new_role = Role(r.id, r.name, r.description, permission_list)
                    roles_list.append(new_role)

                new_owner = User(f.upload.evidence.owner.id, f.upload.evidence.owner.username,
                                 f.upload.evidence.owner.password, f.upload.evidence.owner.first_name,
                                 f.upload.evidence.owner.family_name, f.upload.evidence.owner.email, roles_list)

                new_evidence = Evidence(f.upload.evidence.id, f.upload.evidence.alias, f.upload.evidence.size,
                                        new_owner)

                new_upload = Upload(f.upload.id, f.upload.path, f.upload.size, f.upload.type, new_evidence)

                new_file = File(f.id, f.path, f.size, f.name, f.hash_md5, f.hash_sha256, new_upload)
                file_list.append(new_file)

            return file_list

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def get_file(self, file_id):
        """
        This method retrieves files with given id from DB
        :return: File
        """
        try:
            alchemy_file = self.session.query(AlchemyFile).filter_by(id=file_id).first()

            if alchemy_file is None:
                new_file = None
            else:

                roles_list = list()

                for r in alchemy_file.upload.evidence.owner.roles:
                    permission_list = list()
                    for p in r.permissions:
                        new_permission = Permission(p.id, p.name, p.description)
                        permission_list.append(new_permission)

                    new_role = Role(r.id, r.name, r.description, permission_list)
                    roles_list.append(new_role)

                new_user = User(alchemy_file.upload.evidence.owner.id, alchemy_file.upload.evidence.owner.username,
                                alchemy_file.upload.evidence.owner.password,
                                alchemy_file.upload.evidence.owner.first_name,
                                alchemy_file.upload.evidence.owner.family_name,
                                alchemy_file.upload.evidence.owner.email, roles_list)

                new_evidence = Evidence(alchemy_file.upload.evidence.id, alchemy_file.upload.evidence.alias,
                                        alchemy_file.upload.evidence.size, new_user)

                new_upload = Upload(alchemy_file.upload.id, alchemy_file.upload.path, alchemy_file.upload.size,
                                    alchemy_file.upload.type, new_evidence)

                new_file = File(alchemy_file.id, alchemy_file.path, alchemy_file.size, alchemy_file.name,
                                alchemy_file.hash_md5, alchemy_file.hash_sha256, new_upload)

            return new_file

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def create_file(self, path, size, name, hash_md5, hash_sha256, upload):
        """
        This method inserts a new alchemy file in DB
        :return: File, Boolean
        """
        try:
            alchemy_upload = self.alchemy_get_upload(upload.id)
            alchemy_file = AlchemyFile(path, size, name, hash_md5, hash_sha256)
            alchemy_file.upload = alchemy_upload

            self.session.add(alchemy_file)

            self.session.commit()

            file = File(alchemy_file.id, alchemy_file.path, alchemy_file.size, alchemy_file.name, alchemy_file.hash_md5,
                        alchemy_file.hash_sha256, upload)

            return file, True

        except Exception:
            return None, False

    def get_all_entities(self):
        """
        This method retrieves all entities from DB
        :return: {Entity}
        """
        try:
            alchemy_entities_list = self.session.query(AlchemyEntity).all()

            entities_list = list()

            for ent in alchemy_entities_list:
                new_entity = Entity(ent.id, ent.name, ent.description)
                entities_list.append(new_entity)

            return entities_list

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def get_entity(self, entity_id):
        """
        This method retrieves entity with given id from DB
        :return: Entity
        """
        try:
            alchemy_entity = self.session.query(AlchemyEntity).filter_by(id=entity_id).first()

            if alchemy_entity is None:
                new_entity = None
            else:
                new_entity = Entity(alchemy_entity.id, alchemy_entity.name, alchemy_entity.description)

            return new_entity

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def create_entity(self, name, description):
        """
        This method inserts a new alchemy entity in DB
        :return: {Entity, Boolean}
        """
        try:
            alchemy_entity = AlchemyEntity(name, description)

            self.session.add(alchemy_entity)
            self.session.commit()

            entity = Entity(alchemy_entity.id, alchemy_entity.name, alchemy_entity.description)

            return entity, True

        except Exception:
            return None, False

    def alchemy_get_entity(self, entity_id):
        """
        This method retrieves an alchemy entity with given id from DB
        Not included in views (not published)
        :return: {AlchemyEntity}
        """
        try:
            alchemy_entity = self.session.query(AlchemyEntity).filter_by(id=entity_id).first()

            return alchemy_entity

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def get_all_instances(self, entity_id):
        """
        This method retrieves all instances from DB that belongs to entity_id
        :return: {Instance}
        """
        try:
            alchemy_instance_list = self.session.query(AlchemyInstance).filter_by(entity_id=entity_id).all()
            instance_list = list()

            for ins in alchemy_instance_list:
                new_entity = Entity(ins.entity.id, ins.entity.name, ins.entity.description)
                new_instance = Instance(ins.id, ins.name, new_entity)
                instance_list.append(new_instance)

            return instance_list

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def get_instance(self, instance_id):
        """
        This method retrieves instances with given id from DB
        :return: Instance
        """
        try:
            alchemy_instance = self.session.query(AlchemyInstance).filter_by(id=instance_id).first()
            if alchemy_instance is None:
                new_instance = None
            else:
                new_entity = Entity(alchemy_instance.entity.id, alchemy_instance.entity.name,
                                    alchemy_instance.entity.description)
                new_instance = Instance(alchemy_instance.id, alchemy_instance.name, new_entity)

            return new_instance

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def create_instance(self, name, entity):
        """
        This method inserts a new alchemy instance in DB
        :return: Instance, Boolean
        """
        try:
            alchemy_entity = self.alchemy_get_entity(entity.id)

            alchemy_instance = AlchemyInstance(name)
            alchemy_instance.entity = alchemy_entity

            self.session.add(alchemy_instance)
            self.session.commit()

            instance = Instance(alchemy_instance.id, alchemy_instance.name, entity)

            return instance, True

        except Exception:
            return None, False

    def alchemy_get_instance(self, instance_id):
        """
        This method retrieves an alchemy instance with given id from DB
        Not included in views (not published)
        :return: {AlchemyInstance}
        """
        try:
            alchemy_instance = self.session.query(AlchemyInstance).filter_by(id=instance_id).first()

            return alchemy_instance

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def get_all_properties(self, entity_id):
        """
        This method retrieves all properties from DB that belongs to entity_id
        :return: {Property}
        """
        try:
            alchemy_property_list = self.session.query(AlchemyProperty).filter_by(entity_id=entity_id).all()

            property_list = list()

            for prop in alchemy_property_list:
                new_entity = Entity(prop.entity.id, prop.entity.name, prop.entity.description)
                new_property = Property(prop.id, prop.name, prop.description, new_entity)
                property_list.append(new_property)

            return property_list

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def get_property(self, property_id):
        """
        This method retrieves properties with given id from DB
        :return: Property
        """
        try:
            alchemy_property = self.session.query(AlchemyProperty).filter_by(id=property_id).first()
            if alchemy_property is None:
                new_property = None
            else:
                new_entity = Entity(alchemy_property.entity.id, alchemy_property.entity.name,
                                    alchemy_property.entity.description)
                new_property = Property(alchemy_property.id, alchemy_property.name, alchemy_property.description,
                                        new_entity)

            return new_property

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def create_property(self, name, description, entity):
        """
        This method inserts a new alchemy property in DB
        :return: Property, Boolean
        """
        try:
            alchemy_entity = self.alchemy_get_entity(entity.id)

            alchemy_property = AlchemyProperty(name, description)
            alchemy_property.entity = alchemy_entity

            self.session.add(alchemy_property)
            self.session.commit()

            property = Property(alchemy_property.id, alchemy_property.name, alchemy_property.description, entity)

            return property, True

        except Exception:
            return None, False

    def alchemy_get_property(self, property_id):
        """
        This method retrieves an alchemy property with given id from DB
        Not included in views (not published)
        :return: {AlchemyEntity}
        """
        try:
            alchemy_property = self.session.query(AlchemyProperty).filter_by(id=property_id).first()

            return alchemy_property

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def get_all_values(self, instance_id):
        """
        This method retrieves all values from DB that belongs to instance_id
        :return: {Value}
        """
        try:
            alchemy_value_list = self.session.query(AlchemyValue).filter_by(instance_id=instance_id).all()

            value_list = list()

            for val in alchemy_value_list:
                new_entity = Entity(val.property.entity.id, val.property.entity.name, val.property.entity.description)
                new_property = Property(val.property.id, val.property.name, val.property.description, new_entity)
                new_instance = Instance(val.instance.id, val.instance.name, new_entity)
                new_value = Value(val.id, new_property, new_instance, val.value)
                value_list.append(new_value)

            return value_list

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def get_value(self, value_id):
        """
        This method retrieves values with given id from DB
        :return: Value
        """
        try:
            alchemy_value = self.session.query(AlchemyValue).filter_by(id=value_id).first()

            if alchemy_value is None:
                new_value = None
            else:
                new_entity = Entity(alchemy_value.property.entity.id, alchemy_value.property.entity.name,
                                    alchemy_value.property.entity.description)
                new_property = Property(alchemy_value.property.id, alchemy_value.property.name,
                                        alchemy_value.property.description, new_entity)
                new_instance = Instance(alchemy_value.instance.id, alchemy_value.instance.name, new_entity)
                new_value = Value(alchemy_value.id, new_property, new_instance, alchemy_value.value)

            return new_value

        except Exception as e:
            raise AppException(GenericErrorMessages.DATABASE_ERROR + ': ' + str(e))

    def create_value(self, property, instance, value):
        """
        This method inserts a new alchemy value in DB
        :return: Value, Boolean
        """
        try:
            # Check that instance adn property refer same entity
            if property.entity.id != instance.entity.id:
                return None, False
            alchemy_property = self.alchemy_get_property(property.id)
            alchemy_instance = self.alchemy_get_instance(instance.id)

            alchemy_value = AlchemyValue(value)
            alchemy_value.property = alchemy_property
            alchemy_value.instance = alchemy_instance

            self.session.add(alchemy_value)
            self.session.commit()

            value = Value(alchemy_value.id, property, instance, value)

            return value, True

        except Exception:
            return None, False

    def get_base_engine(self):
        """
        This method returns Base class and engine
        :return: Base, Engine
        """
        return Base, self.engine
