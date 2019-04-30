import logging
from common.infra_tools.decorators import log_function
from nose.tools import assert_equal, assert_true
from sky_modules.datasource_module.datasource_module import DatasourceModule, MODULE_NAME
from sky_modules.datasource_module.model_datasource_module import Permission, Role, User, CaseType, CaseStatus, Case, \
    Evidence, Upload, File, Entity, Instance, Property, Value
from common import config
import datetime

logger = logging.getLogger(MODULE_NAME)


class TestDatasourceModule(object):
    module = None

    def __init__(self):
        pass

    @classmethod
    def setup_class(cls):
        """
        This method is run once for each class before any tests are run
        """
        TestDatasourceModule.module = DatasourceModule(config, MODULE_NAME)

        # Create permissions
        cls.module.create_permission('p1', 'init_pppp1')
        cls.module.create_permission('p2', 'init_pppp2')
        cls.module.create_permission('p3', 'init_pppp3')

        # Create roles
        permission_list = list()
        per = cls.module.get_permission(1)
        permission_list.append(per)
        per2 = cls.module.get_permission(2)
        permission_list.append(per2)

        cls.module.create_role('init_name', 'init_des', permission_list)
        permission_list = list()
        per3 = cls.module.get_permission(3)
        permission_list.append(per2)
        permission_list.append(per3)
        cls.module.create_role('role2', 'desc_role 2', permission_list)

        # Create users
        roles_list = list()
        r1 = cls.module.get_role(1)
        r2 = cls.module.get_role(2)
        roles_list.append(r1)
        cls.module.create_user('ini_user', 'ini_passwd', 'ini_first', 'ini_fam', 'ini_email', roles_list)
        roles_list.append(r2)
        cls.module.create_user('ini_user2', 'ini_passwd2', 'ini_first2', 'ini_fam2', 'ini_email2', roles_list)

        # Create case types
        cls.module.create_case_type('ctype 1', 'case descrp 1')
        cls.module.create_case_type('ctype 2', 'case descrp 2')
        cls.module.create_case_type('ctype 3', 'case descrp 3')

        # Create case status
        cls.module.create_case_status('cstatus 1', 'status descrp 1')
        cls.module.create_case_status('cstatus 2', 'status descrp 2')
        cls.module.create_case_status('cstatus 3', 'status descrp 3')

        # Create case
        case_type = cls.module.get_case_type(2)
        case_status = cls.module.get_case_status(1)
        cls.module.create_case('formal1', 'friend1', datetime.datetime.now(), 1, 2, 3, 4, 5, 6, case_type, case_status)

        case_type = cls.module.get_case_type(3)
        case_status = cls.module.get_case_status(2)
        cls.module.create_case('formal2', 'friend2', datetime.datetime.now(), 7, 8, 9, 10, 11, 12, case_type,
                               case_status)

        # Create evidence
        owner1 = cls.module.get_user(1)
        owner2 = cls.module.get_user(2)
        cls.module.create_evidence('alias 1', 11.1, owner1)
        cls.module.create_evidence('alias 2', 22.2, owner2)

        # Create upload
        evidence1 = cls.module.get_evidence(1)
        evidence2 = cls.module.get_evidence(2)

        cls.module.create_upload('path 11', 123.1, 'type 11', evidence1)
        cls.module.create_upload('path 12', 256.32, 'type 12', evidence1)

        cls.module.create_upload('path 21', 0.65, 'type 21', evidence2)
        cls.module.create_upload('path 22', 512.2, 'type 22', evidence2)
        cls.module.create_upload('path 23', 1.45, 'type 23', evidence2)
        cls.module.create_upload('path 24', 1024.65, 'type 24', evidence2)

        # Create file
        upload1 = cls.module.get_upload(1)
        upload2 = cls.module.get_upload(2)

        cls.module.create_file('file path 11', 1.11, 'file name 11', 'file has 5 11', 'file has256 11', upload1)
        cls.module.create_file('file path 12', 2.22, 'file name 12', 'file has 5 12', 'file has256 12', upload1)

        cls.module.create_file('file path 21', 101.11, 'file name 21', 'file has 5 21', 'file has256 21', upload2)
        cls.module.create_file('file path 22', 102.22, 'file name 22', 'file has 5 22', 'file has256 22', upload2)
        cls.module.create_file('file path 23', 103.33, 'file name 23', 'file has 5 23', 'file has256 23', upload2)

        # Create entity
        entity1 = cls.module.create_entity('ent name 1', 'ent desc 1')
        entity2 = cls.module.create_entity('ent name 2', 'ent desc 2')

        # Create instances
        instance1 = cls.module.create_instance("instance 11", entity1[0])
        cls.module.create_instance("instance 12", entity1[0])
        cls.module.create_instance("instance 13", entity1[0])

        instance2 = cls.module.create_instance("instance 21", entity2[0])
        cls.module.create_instance("instance 22", entity2[0])

        # Create properties
        property11 = cls.module.create_property('pro name 11', 'pro desc 11', entity1[0])
        property12 = cls.module.create_property('pro name 12', 'pro desc 12', entity1[0])
        property13 = cls.module.create_property('pro name 13', 'pro desc 13', entity1[0])

        property21 = cls.module.create_property('pro name 21', 'pro desc 21', entity2[0])
        property22 = cls.module.create_property('pro name 22', 'pro desc 22', entity2[0])
        property23 = cls.module.create_property('pro name 23', 'pro desc 23', entity2[0])
        property24 = cls.module.create_property('pro name 24', 'pro desc 24', entity2[0])

        # Create values
        cls.module.create_value(property11[0], instance1[0], 'value 11')
        cls.module.create_value(property12[0], instance1[0], 'value 12')
        cls.module.create_value(property13[0], instance1[0], 'value 13')

        cls.module.create_value(property21[0], instance2[0], 'value 21')
        cls.module.create_value(property22[0], instance2[0], 'value 22')
        cls.module.create_value(property23[0], instance2[0], 'value 23')
        cls.module.create_value(property24[0], instance2[0], 'value 24')

    @classmethod
    def teardown_class(cls):
        """
        This method is run once for each class _after_ all tests are run
        """
        base, eng = cls.module.get_base_engine()

        base.metadata.drop_all(eng)

    def setup(self):
        """
        This method is run once before _each_ test method is executed
        """
        pass

    def teardown(self):
        """
        This method is run once after _each_ test method is executed
        """
        pass

    @log_function(logger)
    def test_01_get_permission(self):
        permission_list = self.module.get_all_permissions()

        assert_true(type(permission_list) is list)
        for p in permission_list:
            assert_true(type(p) is Permission)
        assert_true(len(permission_list) == 3)
        assert_equal(permission_list[0].name, 'p1')
        assert_equal(permission_list[0].description, 'init_pppp1')
        assert_equal(permission_list[1].name, 'p2')
        assert_equal(permission_list[1].description, 'init_pppp2')
        assert_equal(permission_list[2].name, 'p3')
        assert_equal(permission_list[2].description, 'init_pppp3')

    @log_function(logger)
    def test_02_get_role(self):
        roles_list = self.module.get_all_roles()
        assert_true(type(roles_list) is list)
        for r in roles_list:
            assert_true(type(r) is Role)
            assert_true(type(r.permissions) is list)
            for p in r.permissions:
                assert_true(type(p) is Permission)

        role_2 = self.module.get_role(2)
        assert_true(type(role_2) is Role)
        assert_true(type(role_2.permissions) is list)
        for p in role_2.permissions:
            assert_true(type(p) is Permission)
        role_found = None
        for r in roles_list:
            if r.id == 2:
                role_found = r
                break
        assert_true(len(roles_list) == 2)
        assert_true(role_found is not None)
        assert_equal(role_found.id, 2)
        assert_equal(role_found.id, role_2.id)
        assert_equal(role_found.name, role_2.name)
        assert_equal(role_found.description, role_2.description)
        assert_equal(len(role_found.permissions), len(role_2.permissions))

        long = len(role_found.permissions)
        for index in range(long):
            assert_equal(role_found.permissions[index].id, role_2.permissions[index].id)
            assert_equal(role_found.permissions[index].name, role_2.permissions[index].name)
            assert_equal(role_found.permissions[index].description, role_2.permissions[index].description)

    @log_function(logger)
    def test_03_get_user(self):
        users_list = self.module.get_all_users()
        assert_true(type(users_list) is list)
        for u in users_list:
            assert_true(type(u) is User)
            assert_true(type(u.roles) is list)
            for r in u.roles:
                assert_true(type(r) is Role)
                assert_true(type(u.roles) is list)
                for p in r.permissions:
                    assert_true(type(p) is Permission)

        user_1 = self.module.get_user(1)
        assert_true(type(user_1) is User)
        assert_true(type(user_1.roles) is list)
        for r in user_1.roles:
            assert_true(type(r) is Role)
            assert_true(type(r.permissions) is list)
            for p in r.permissions:
                assert_true(type(p) is Permission)

        user_found = None

        for u in users_list:
            if u.id == 1:
                user_found = u
                break

        assert_true(len(users_list) == 2)
        assert_true(user_found is not None)
        assert_equal(user_found.id, user_1.id)
        assert_equal(user_found.username, user_1.username)
        assert_equal(user_found.password, user_1.password)
        assert_equal(user_found.first_name, user_1.first_name)
        assert_equal(user_found.family_name, user_1.family_name)
        assert_equal(user_found.email, user_1.email)
        assert_equal(len(user_found.roles), len(user_1.roles))

        long = len(user_found.roles)
        for index in range(long):
            assert_equal(user_found.roles[index].id, user_1.roles[index].id)
            assert_equal(user_found.roles[index].name, user_1.roles[index].name)
            assert_equal(user_found.roles[index].description, user_1.roles[index].description)

    @log_function(logger)
    def test_04_get_case_type(self):
        case_types_list = self.module.get_all_case_types()
        assert_true(type(case_types_list) is list)
        for ct in case_types_list:
            assert_true(type(ct) is CaseType)
        type_3 = self.module.get_case_type(3)
        assert_true(type(type_3) is CaseType)
        type_found = None

        for t in case_types_list:
            if t.id == 3:
                type_found = t
                break

        assert_true(len(case_types_list) == 3)
        assert_true(type_found is not None)
        assert_equal(type_found.id, type_3.id)
        assert_equal(type_found.name, type_3.name)
        assert_equal(type_found.description, type_3.description)

    @log_function(logger)
    def test_05_get_case_status(self):
        case_status_list = self.module.get_all_case_status()
        assert_true(type(case_status_list) is list)
        for cs in case_status_list:
            assert_true(type(cs) is CaseStatus)
        status_2 = self.module.get_case_status(2)
        assert_true(type(status_2) is CaseStatus)
        status_found = None

        for s in case_status_list:
            if s.id == 2:
                status_found = s
                break

        assert_true(status_found is not None)
        assert_true(len(case_status_list) == 3)
        assert_equal(status_found.id, status_2.id)
        assert_equal(status_found.name, status_2.name)
        assert_equal(status_found.description, status_2.description)

    @log_function(logger)
    def test_06_get_case(self):
        case_list = self.module.get_all_cases()
        assert_true(type(case_list) is list)
        for c in case_list:
            assert_true(type(c) is Case)
            assert_true(type(c.case_type) is CaseType)
            assert_true(type(c.case_status) is CaseStatus)
        case_2 = self.module.get_case(2)
        assert_true(type(case_2) is Case)
        assert_true(type(case_2.case_type) is CaseType)
        assert_true(type(case_2.case_status) is CaseStatus)
        case_found = None

        for c in case_list:
            if c.id == 2:
                case_found = c
                break

        assert_true(len(case_list) == 2)
        assert_equal(case_found.id, case_2.id)
        assert_equal(case_found.formal_name, case_2.formal_name)
        assert_equal(case_found.friend_name, case_2.friend_name)
        assert_equal(case_found.creation_datetime, case_2.creation_datetime)
        assert_equal(case_found.num_win, case_2.num_win)
        assert_equal(case_found.num_lin, case_2.num_lin)
        assert_equal(case_found.num_ios, case_2.num_ios)
        assert_equal(case_found.num_mal, case_2.num_mal)
        assert_equal(case_found.num_pac, case_2.num_pac)
        assert_equal(case_found.num_log, case_2.num_log)

        assert_equal(case_found.case_type.id, case_2.case_type.id)
        assert_equal(case_found.case_type.name, case_2.case_type.name)
        assert_equal(case_found.case_type.description, case_2.case_type.description)

        assert_equal(case_found.case_status.id, case_2.case_status.id)
        assert_equal(case_found.case_status.name, case_2.case_status.name)
        assert_equal(case_found.case_status.description, case_2.case_status.description)

    @log_function(logger)
    def test_07_get_evidence(self):
        evidence_list = self.module.get_all_evidences()
        assert_true(type(evidence_list) is list)
        for e in evidence_list:
            assert_true(type(e) is Evidence)
            assert_true(type(e.owner) is User)
        evidence_1 = self.module.get_evidence(1)
        assert_true(type(evidence_1) is Evidence)
        assert_true(type(evidence_1.owner) is User)
        evidence_found = None

        for e in evidence_list:
            if e.id == 1:
                evidence_found = e
                break

        assert_true(len(evidence_list) == 2)
        assert_true(evidence_found is not None)
        assert_equal(evidence_found.id, evidence_1.id)
        assert_equal(evidence_found.alias, evidence_1.alias)
        assert_equal(evidence_found.size, evidence_1.size)

        assert_equal(evidence_found.owner.id, evidence_1.owner.id)
        assert_equal(evidence_found.owner.username, evidence_1.owner.username)
        assert_equal(evidence_found.owner.password, evidence_1.owner.password)
        assert_equal(evidence_found.owner.first_name, evidence_1.owner.first_name)
        assert_equal(evidence_found.owner.family_name, evidence_1.owner.family_name)
        assert_equal(evidence_found.owner.email, evidence_1.owner.email)

    @log_function(logger)
    def test_08_get_upload(self):
        upload_list = self.module.get_all_uploads(2)
        assert_true(type(upload_list) is list)
        for u in upload_list:
            assert_true(type(u) is Upload)
            assert_true(type(u.evidence) is Evidence)
        upload_5 = self.module.get_upload(5)
        assert_true(type(upload_5) is Upload)
        assert_true(type(upload_5.evidence) is Evidence)
        upload_found = None

        for u in upload_list:
            if u.id == 5:
                upload_found = u
                break

        assert_true(len(upload_list) == 4)
        assert_true(upload_found is not None)
        assert_equal(upload_found.id, upload_5.id)
        assert_equal(upload_found.path, upload_5.path)
        assert_equal(upload_found.size, upload_5.size)
        assert_equal(upload_found.type, upload_5.type)

        assert_equal(upload_found.evidence.id, upload_5.evidence.id)
        assert_equal(upload_found.evidence.alias, upload_5.evidence.alias)
        assert_equal(upload_found.evidence.size, upload_5.evidence.size)

    @log_function(logger)
    def test_09_get_file(self):
        file_list = self.module.get_all_files(2)
        assert_true(type(file_list) is list)
        for f in file_list:
            assert_true(type(f) is File)
            assert_true(type(f.upload) is Upload)
        file_4 = self.module.get_file(4)
        assert_true(type(file_4) is File)
        assert_true(type(file_4.upload) is Upload)
        file_found = None

        for f in file_list:
            if f.id == 4:
                file_found = f
                break

        assert_true(len(file_list) == 3)
        assert_true(file_found is not None)
        assert_equal(file_found.id, file_4.id)
        assert_equal(file_found.path, file_4.path)
        assert_equal(file_found.size, file_4.size)
        assert_equal(file_found.name, file_4.name)
        assert_equal(file_found.hash_md5, file_4.hash_md5)
        assert_equal(file_found.hash_sha256, file_4.hash_sha256)

        assert_equal(file_found.upload.id, file_4.upload.id)
        assert_equal(file_found.upload.size, file_4.upload.size)
        assert_equal(file_found.upload.type, file_4.upload.type)

    @log_function(logger)
    def test_10_get_entity(self):
        entity_list = self.module.get_all_entities()
        assert_true(type(entity_list) is list)
        for e in entity_list:
            assert_true(type(e) is Entity)

        assert_true(len(entity_list) == 2)

        assert_equal(entity_list[0].name, 'ent name 1')
        assert_equal(entity_list[0].description, 'ent desc 1')
        assert_equal(entity_list[1].name, 'ent name 2')
        assert_equal(entity_list[1].description, 'ent desc 2')

    @log_function(logger)
    def test_11_get_instance(self):
        instance_list = self.module.get_all_instances(1)
        assert_true(type(instance_list) is list)
        for i in instance_list:
            assert_true(type(i) is Instance)
            assert_true(type(i.entity) is Entity)
        instance_2 = self.module.get_instance(2)
        assert_true(type(instance_2) is Instance)
        assert_true(type(instance_2.entity) is Entity)
        instance_found = None

        for i in instance_list:
            if i.id == 2:
                instance_found = i
                break

        assert_true(len(instance_list) == 3)
        assert_true(instance_found is not None)
        assert_equal(instance_found.id, instance_2.id)
        assert_equal(instance_found.name, instance_2.name)

        assert_equal(instance_found.entity.id, instance_2.entity.id)
        assert_equal(instance_found.entity.name, instance_2.entity.name)
        assert_equal(instance_found.entity.description, instance_2.entity.description)

    @log_function(logger)
    def test_12_get_property(self):
        property_list = self.module.get_all_properties(2)
        assert_true(type(property_list) is list)
        for p in property_list:
            assert_true(type(p) is Property)
            assert_true(type(p.entity) is Entity)
        property_6 = self.module.get_property(6)
        assert_true(type(property_6) is Property)
        assert_true(type(property_6.entity) is Entity)
        property_found = None

        for p in property_list:
            if p.id == 6:
                property_found = p
                break

        assert_true(len(property_list) == 4)
        assert_true(property_found is not None)
        assert_equal(property_found.id, property_6.id)
        assert_equal(property_found.name, property_6.name)
        assert_equal(property_found.description, property_6.description)

        assert_equal(property_found.entity.id, property_6.entity.id)
        assert_equal(property_found.entity.name, property_6.entity.name)
        assert_equal(property_found.entity.description, property_6.entity.description)

    @log_function(logger)
    def test_13_get_value(self):
        value_list = self.module.get_all_values(4)
        assert_true(type(value_list) is list)
        for v in value_list:
            assert_true(type(v) is Value)
            assert_true(type(v.property) is Property)
            assert_true(type(v.instance) is Instance)
        value_4 = self.module.get_value(4)
        assert_true(type(value_4) is Value)
        assert_true(type(value_4.property) is Property)
        assert_true(type(value_4.instance) is Instance)
        value_found = None

        for v in value_list:
            if v.id == 4:
                value_found = v

        assert_true(len(value_list) == 4)
        assert_true(value_found is not None)
        assert_equal(value_found.id, value_4.id)
        assert_equal(value_found.value, value_4.value)

        assert_equal(value_found.property.id, value_4.property.id)

        assert_equal(value_found.instance.id, value_4.instance.id)

        assert_equal(value_found.instance.entity.id, value_4.instance.entity.id)

    @log_function(logger)
    def test_14_set_permission(self):
        name = 'test name 1'
        description = 'test desc 1'
        new_permission = self.module.create_permission(name, description)
        new_id = new_permission[0].id

        permission_list = self.module.get_all_permissions()
        assert_true(type(permission_list) is list)
        for p in permission_list:
            assert_true(type(p) is Permission)

        permission_found = None

        for p in permission_list:
            if p.id == new_id:
                permission_found = p
                break

        assert_true(new_permission[1])
        assert_true(permission_found is not None)
        assert_true(type(new_permission[0]) is Permission)
        assert_equal(permission_found.id, new_id)
        assert_equal(permission_found.name, name)
        assert_equal(permission_found.description, description)

    @log_function(logger)
    def test_15_set_role(self):
        perm_1_name = 'perm 1 name'
        perm_1_description = 'perm 1 desc'
        perm_2_name = 'perm 2 name'
        perm_2_description = 'perm 2 desc'
        role_name = 'role name'
        role_description = 'role description'

        perm_names = list()
        perm_names.append(perm_1_name)
        perm_names.append(perm_2_name)

        perm_desc = list()
        perm_desc.append(perm_1_description)
        perm_desc.append(perm_2_description)

        new_permission_1 = self.module.create_permission(perm_1_name, perm_1_description)
        assert_true(new_permission_1[0] is not None)
        assert_true(new_permission_1[1])
        assert_true(type(new_permission_1[0]) is Permission)
        new_permission_2 = self.module.create_permission(perm_2_name, perm_2_description)
        assert_true(new_permission_2[0] is not None)
        assert_true(new_permission_2[1])
        assert_true(type(new_permission_2[0]) is Permission)

        permission_list = list()
        permission_list.append(new_permission_1[0])
        permission_list.append(new_permission_2[0])

        new_role = self.module.create_role(role_name, role_description, permission_list)
        assert_true(new_role[0] is not None)
        assert_true(new_role[1])
        assert_true(type(new_role[0]) is Role)
        for p in new_role[0].permissions:
            assert_true(type(p) is Permission)

        new_role_id = new_role[0].id

        role_found = self.module.get_role(new_role_id)
        assert_true(role_found is not None)
        assert_equal(role_found.id, new_role_id)

        assert_true(type(role_found) is Role)
        assert_true(type(role_found.permissions) is list)
        for p in role_found.permissions:
            assert_true(type(p) is Permission)

        assert_equal(role_found.name, role_name)
        assert_equal(role_found.description, role_description)

        assert_equal(len(role_found.permissions), len(permission_list))
        long_lista = len(role_found.permissions)

        for index in range(long_lista):
            assert_equal(role_found.permissions[index].id, permission_list[index].id)
            assert_equal(role_found.permissions[index].name, perm_names[index])
            assert_equal(role_found.permissions[index].description, perm_desc[index])

    @log_function(logger)
    def test_16_set_user(self):
        username = 'test user username 1'
        password = 'test user password 1'
        first_name = 'test user first 1'
        family_name = 'test user family 1'
        email = 'test user email 1'

        permission_list = self.module.get_all_permissions()
        assert_true(type(permission_list) is list)
        for p in permission_list:
            assert_true(type(p) is Permission)

        perm_1 = permission_list[0]
        perm_2 = permission_list[1]
        perm_3 = permission_list[2]

        pl1 = list()
        pl1.append(perm_1)
        pl1.append(perm_3)

        pl2 = list()
        pl2.append(perm_1)
        pl2.append(perm_2)
        pl2.append(perm_3)

        role_1_name = 'role 1 name'
        role_1_description = 'role 1 description'
        role_2_name = 'role 2 name'
        role_2_description = 'role 2 description'

        role_1_tuple = self.module.create_role(role_1_name, role_1_description, pl1)
        assert_true(role_1_tuple[0] is not None)
        assert_true(role_1_tuple[1])
        assert_true(type(role_1_tuple[0]) is Role)
        for p in role_1_tuple[0].permissions:
            assert_true(type(p) is Permission)

        role_2_tuple = self.module.create_role(role_2_name, role_2_description, pl2)
        assert_true(role_2_tuple[0] is not None)
        assert_true(role_2_tuple[1])
        assert_true(type(role_2_tuple[0]) is Role)
        for p in role_2_tuple[0].permissions:
            assert_true(type(p) is Permission)

        roles_list = list()
        roles_list.append(role_1_tuple[0])
        roles_list.append(role_2_tuple[0])

        new_user_tuple = self.module.create_user(username, password, first_name, family_name, email, roles_list)
        assert_true(new_user_tuple[0] is not None)
        assert_true(new_user_tuple[1])
        new_user = new_user_tuple[0]
        assert_true(type(new_user) is User)
        assert_true(type(new_user.roles) is list)
        for r in new_user.roles:
            assert_true(type(r) is Role)
            assert_true(type(r.permissions) is list)
            for p in r.permissions:
                assert_true(type(p) is Permission)

        user_found = self.module.get_user(new_user.id)

        assert_true(type(user_found) is User)
        assert_true(type(user_found.roles) is list)
        for r in user_found.roles:
            assert_true(type(r) is Role)
            assert_true(type(r.permissions) is list)
            for p in r.permissions:
                assert_true(type(p) is Permission)

        assert_true(user_found is not None)
        assert_equal(user_found.id, new_user.id)
        assert_equal(user_found.username, username)
        assert_equal(user_found.password, password)
        assert_equal(user_found.first_name, first_name)
        assert_equal(user_found.family_name, family_name)
        assert_equal(user_found.email, email)

        assert_equal(len(user_found.roles), len(new_user.roles))
        long_roles = len(user_found.roles)

        for index in range(long_roles):
            assert_equal(user_found.roles[index].id, new_user.roles[index].id)
            assert_equal(user_found.roles[index].name, new_user.roles[index].name)
            assert_equal(user_found.roles[index].description, new_user.roles[index].description)
            assert_equal(len(user_found.roles[index].permissions), len(new_user.roles[index].permissions))

    @log_function(logger)
    def test_17_set_case_type(self):
        case_type_name = 'case type name'
        case_type_desc = 'case type desc'
        case_type_tuple = self.module.create_case_type(case_type_name, case_type_desc)
        new_case_type = case_type_tuple[0]
        assert_true(new_case_type is not None)
        assert_true(case_type_tuple[1])
        assert_true(type(new_case_type) is CaseType)

        case_type_found = self.module.get_case_type(new_case_type.id)
        assert_true(case_type_found is not None)
        assert_true(type(case_type_found) is CaseType)
        assert_equal(case_type_found.id, new_case_type.id)
        assert_equal(case_type_found.name, case_type_name)
        assert_equal(case_type_found.description, case_type_desc)

    @log_function(logger)
    def test_18_set_case_status(self):

        case_status_name = 'case status name'
        case_status_desc = 'case status desc'
        case_status_tuple = self.module.create_case_status(case_status_name, case_status_desc)
        new_case_status = case_status_tuple[0]
        assert_true(new_case_status is not None)
        assert_true(case_status_tuple[1])
        assert_true(type(new_case_status) is CaseStatus)

        case_status_found = self.module.get_case_status(new_case_status.id)
        assert_true(case_status_found is not None)
        assert_true(type(case_status_found) is CaseStatus)
        assert_equal(case_status_found.id, new_case_status.id)
        assert_equal(case_status_found.name, case_status_name)
        assert_equal(case_status_found.description, case_status_desc)

    @log_function(logger)
    def test_19_set_case(self):
        formal_name = 'case formal name'
        friend_name = 'case friend name'
        creation_datetime = datetime.datetime.now()
        num_win = 1
        num_lin = 2
        num_ios = 3
        num_mal = 4
        num_pac = 5
        num_log = 6

        case_type_name = 'case type name'
        case_type_desc = 'case type desc'
        case_status_name = 'case status name'
        case_status_desc = 'case status desc'

        new_case_type_tuple = self.module.create_case_type(case_type_name, case_type_desc)
        new_case_type = new_case_type_tuple[0]
        assert_true(new_case_type is not None)
        assert_true(new_case_type_tuple[1])
        assert_true(type(new_case_type) is CaseType)

        new_case_status_tuple = self.module.create_case_status(case_status_name, case_status_desc)
        new_case_status = new_case_status_tuple[0]
        assert_true(new_case_status is not None)
        assert_true(new_case_status_tuple[1])
        assert_true(type(new_case_status) is CaseStatus)

        new_case_tuple = self.module.create_case(formal_name, friend_name, creation_datetime, num_win, num_lin,
                                                 num_ios, num_mal, num_pac, num_log, new_case_type, new_case_status)
        new_case = new_case_tuple[0]
        assert_true(new_case is not None)
        assert_true(new_case_status)

        case_found = self.module.get_case(new_case.id)
        assert_true(case_found is not None)
        assert_true(type(case_found) is Case)
        assert_true(type(case_found.case_type) is CaseType)
        assert_true(type(case_found.case_status) is CaseStatus)

        assert_equal(case_found.id, new_case.id)
        assert_equal(case_found.formal_name, formal_name)
        assert_equal(case_found.friend_name, friend_name)
        assert_equal(case_found.creation_datetime, creation_datetime)
        assert_equal(case_found.num_win, num_win)
        assert_equal(case_found.num_lin, num_lin)
        assert_equal(case_found.num_ios, num_ios)
        assert_equal(case_found.num_mal, num_mal)
        assert_equal(case_found.num_pac, num_pac)
        assert_equal(case_found.num_log, num_log)

        assert_equal(case_found.case_type.id, new_case_type.id)
        assert_equal(case_found.case_type.name, case_type_name)
        assert_equal(case_found.case_type.description, case_type_desc)

        assert_equal(case_found.case_status.id, new_case_status.id)
        assert_equal(case_found.case_status.name, case_status_name)
        assert_equal(case_found.case_status.description, case_status_desc)

    @log_function(logger)
    def test_20_set_evidence(self):
        username = 'evidence username'
        password = 'evidence password'
        first_name = 'evidence first name'
        family_name = 'evidence family name'
        email = 'evidence email'

        role_1 = self.module.get_role(1)
        role_2 = self.module.get_role(2)
        roles_list = list()
        roles_list.append(role_1)
        roles_list.append(role_2)
        new_user_tuple = self.module.create_user(username, password, first_name, family_name, email, roles_list)
        new_user = new_user_tuple[0]
        assert_true(new_user is not None)
        assert_true(new_user_tuple[1])
        assert_true(type(new_user) is User)
        assert_true(type(new_user.roles) is list)
        for r in new_user.roles:
            assert_true(type(r) is Role)
            assert_true(type(r.permissions) is list)
            for p in r.permissions:
                assert_true(type(p) is Permission)

        alias = 'evidence alias'
        size = 89.65

        new_evidence_tuple = self.module.create_evidence(alias, size, new_user)
        new_evidence = new_evidence_tuple[0]
        assert_true(new_evidence is not None)
        assert_true(new_evidence_tuple[1])
        assert_true(type(new_evidence) is Evidence)
        assert_true(type(new_evidence.owner) is User)
        assert_true(type(new_evidence.owner.roles) is list)
        for r in new_evidence.owner.roles:
            assert_true(type(r) is Role)
            assert_true(type(r.permissions) is list)
            for p in r.permissions:
                assert_true(type(p) is Permission)

        evidence_found = self.module.get_evidence(new_evidence.id)
        assert_true(evidence_found is not None)

        assert_true(type(evidence_found) is Evidence)
        assert_true(type(evidence_found.owner) is User)
        assert_true(type(evidence_found.owner.roles) is list)
        for r in evidence_found.owner.roles:
            assert_true(type(r) is Role)
            assert_true(type(r.permissions) is list)
            for p in r.permissions:
                assert_true(type(p) is Permission)

        assert_equal(evidence_found.id, new_evidence.id)
        assert_equal(evidence_found.alias, alias)
        assert_equal(evidence_found.size, size)

        assert_equal(evidence_found.owner.id, new_evidence.owner.id)
        assert_equal(evidence_found.owner.username, username)
        assert_equal(evidence_found.owner.password, password)
        assert_equal(evidence_found.owner.first_name, first_name)
        assert_equal(evidence_found.owner.family_name, family_name)
        assert_equal(evidence_found.owner.email, email)
        assert_equal(len(evidence_found.owner.roles), len(new_evidence.owner.roles))

    @log_function(logger)
    def test_21_set_upload(self):
        user_found = self.module.get_user(1)
        assert_true(user_found is not None)
        assert_true(type(user_found) is User)

        assert_true(type(user_found.roles) is list)
        for r in user_found.roles:
            assert_true(type(r) is Role)
            assert_true(type(r.permissions) is list)
            for p in r.permissions:
                assert_true(type(p) is Permission)

        alias = 'evidence alias'
        evidence_size = 119.77
        new_evidence_tuple = self.module.create_evidence(alias, evidence_size, user_found)
        new_evidence = new_evidence_tuple[0]
        assert_true(new_evidence is not None)
        assert_true(new_evidence_tuple[1])
        assert_true(type(new_evidence) is Evidence)
        assert_true(type(new_evidence.owner) is User)
        assert_true(type(new_evidence.owner.roles) is list)
        for r in new_evidence.owner.roles:
            assert_true(type(r) is Role)
            assert_true(type(r.permissions) is list)
            for p in r.permissions:
                assert_true(type(p) is Permission)

        path = 'upload path'
        upload_size = 572.23
        upload_type = 'upload type'

        new_upload_tuple = self.module.create_upload(path, upload_size, upload_type, new_evidence)
        new_upload = new_upload_tuple[0]
        assert_true(new_upload is not None)
        assert_true(new_upload_tuple[1])

        assert_true(type(new_upload) is Upload)
        assert_true(type(new_upload.evidence) is Evidence)
        assert_true(type(new_upload.evidence.owner) is User)
        assert_true(type(new_upload.evidence.owner.roles) is list)
        for r in new_upload.evidence.owner.roles:
            assert_true(type(r) is Role)
            assert_true(type(r.permissions) is list)
            for p in r.permissions:
                assert_true(type(p) is Permission)

        upload_found = self.module.get_upload(new_upload.id)
        assert_true(upload_found is not None)

        assert_true(type(upload_found) is Upload)
        assert_true(type(upload_found.evidence) is Evidence)
        assert_true(type(upload_found.evidence.owner) is User)
        assert_true(type(upload_found.evidence.owner.roles) is list)
        for r in upload_found.evidence.owner.roles:
            assert_true(type(r) is Role)
            assert_true(type(r.permissions) is list)
            for p in r.permissions:
                assert_true(type(p) is Permission)

        assert_equal(upload_found.id, new_upload.id)
        assert_equal(upload_found.path, path)
        assert_equal(upload_found.size, upload_size)
        assert_equal(upload_found.type, upload_type)
        assert_equal(upload_found.evidence.id, new_upload.evidence.id)
        assert_equal(upload_found.evidence.alias, alias)
        assert_equal(upload_found.evidence.size, evidence_size)
        assert_equal(upload_found.evidence.owner.id, new_upload.evidence.owner.id)

    @log_function(logger)
    def test_22_set_file(self):
        upload_path = 'upload path'
        upload_size = 123.67
        upload_type = 'upload type'
        evidence_found = self.module.get_evidence(1)
        assert_true(evidence_found is not None)
        assert_true(type(evidence_found) is Evidence)
        assert_true(type(evidence_found.owner) is User)
        assert_true(type(evidence_found.owner.roles) is list)
        for r in evidence_found.owner.roles:
            assert_true(type(r) is Role)
            assert_true(type(r.permissions) is list)
            for p in r.permissions:
                assert_true(type(p) is Permission)

        new_upload_tuple = self.module.create_upload(upload_path, upload_size, upload_type, evidence_found)
        new_upload = new_upload_tuple[0]
        assert_true(new_upload is not None)
        assert_true(new_upload_tuple[1])
        assert_true(type(new_upload) is Upload)
        assert_true(type(new_upload.evidence) is Evidence)
        assert_true(type(new_upload.evidence.owner) is User)
        assert_true(type(new_upload.evidence.owner.roles) is list)
        for r in new_upload.evidence.owner.roles:
            assert_true(type(r) is Role)
            assert_true(type(r.permissions) is list)
            for p in r.permissions:
                assert_true(type(p) is Permission)

        file_path = 'file path'
        file_size = 0.23
        name = 'file name'
        hash_md5 = 'file hash md5'
        hash_sha256 = 'file hash sha256'

        new_file_tuple = self.module.create_file(file_path, file_size, name, hash_md5, hash_sha256, new_upload)
        new_file = new_file_tuple[0]
        assert_true(new_file is not None)
        assert_true(new_file_tuple[1])

        assert_true(type(new_file) is File)
        assert_true(type(new_file.upload) is Upload)
        assert_true(type(new_file.upload.evidence) is Evidence)
        assert_true(type(new_file.upload.evidence.owner) is User)
        assert_true(type(new_file.upload.evidence.owner.roles) is list)
        for r in new_file.upload.evidence.owner.roles:
            assert_true(type(r) is Role)
            assert_true(type(r.permissions) is list)
            for p in r.permissions:
                assert_true(type(p) is Permission)

        file_found = self.module.get_file(new_file.id)
        assert_true(file_found is not None)
        assert_true(type(file_found) is File)
        assert_true(type(file_found.upload) is Upload)
        assert_true(type(file_found.upload.evidence) is Evidence)
        assert_true(type(file_found.upload.evidence.owner) is User)
        assert_true(type(file_found.upload.evidence.owner.roles) is list)
        for r in file_found.upload.evidence.owner.roles:
            assert_true(type(r) is Role)
            assert_true(type(r.permissions) is list)
            for p in r.permissions:
                assert_true(type(p) is Permission)

        assert_equal(file_found.id, new_file.id)
        assert_equal(file_found.path, file_path)
        assert_equal(file_found.size, file_size)
        assert_equal(file_found.name, name)
        assert_equal(file_found.hash_md5, hash_md5)
        assert_equal(file_found.hash_sha256, hash_sha256)

        assert_equal(file_found.upload.id, new_file.upload.id)
        assert_equal(file_found.upload.path, upload_path)
        assert_equal(file_found.upload.size, upload_size)
        assert_equal(file_found.upload.type, upload_type)
        assert_equal(file_found.upload.evidence.id, new_file.upload.evidence.id)

    @log_function(logger)
    def test_23_set_entity(self):
        entity_name = 'entity name'
        entity_desc = 'entity desc'

        new_entity_tuple = self.module.create_entity(entity_name, entity_desc)
        new_entity = new_entity_tuple[0]
        assert_true(new_entity is not None)
        assert_true(new_entity_tuple[1])
        assert_true(type(new_entity) is Entity)

        entity_found = self.module.get_entity(new_entity.id)
        assert_true(entity_found is not None)
        assert_true(type(entity_found) is Entity)
        assert_equal(entity_found.id, new_entity.id)
        assert_equal(entity_found.name, entity_name)
        assert_equal(entity_found.description, entity_desc)

    @log_function(logger)
    def test_24_set_instance(self):
        entity_name = 'entity name'
        entity_desc = 'entity desc'
        new_entity_tuple = self.module.create_entity(entity_name, entity_desc)
        new_entity = new_entity_tuple[0]
        assert_true(new_entity is not None)
        assert_true(new_entity_tuple[1])
        assert_true(type(new_entity) is Entity)

        instance_name = 'instance name'
        new_instance_tuple = self.module.create_instance(instance_name, new_entity)
        new_instance = new_instance_tuple[0]
        assert_true(new_instance is not None)
        assert_true(new_instance_tuple[1])
        assert_true(type(new_instance) is Instance)
        assert_true(type(new_instance.entity) is Entity)

        instance_found = self.module.get_instance(new_instance.id)
        assert_true(instance_found is not None)

        assert_true(type(instance_found) is Instance)
        assert_true(type(instance_found.entity) is Entity)
        assert_equal(instance_found.id, new_instance.id)
        assert_equal(instance_found.name, instance_name)
        assert_equal(instance_found.entity.id, new_entity.id)
        assert_equal(instance_found.entity.name, entity_name)
        assert_equal(instance_found.entity.description, entity_desc)

    @log_function(logger)
    def test_25_set_property(self):

        ent_name = 'ent name'
        ent_desc = 'ent desc'
        new_entity_tuple = self.module.create_entity(ent_name, ent_desc)
        new_entity = new_entity_tuple[0]
        assert_true(new_entity is not None)
        assert_true(new_entity_tuple[1])
        assert_true(type(new_entity) is Entity)

        pro_name = 'pro_name'
        pro_desc = 'pro_desc'
        new_property_tuple = self.module.create_property(pro_name, pro_desc, new_entity)
        new_property = new_property_tuple[0]
        assert_true(new_property is not None)
        assert_true(new_property_tuple[1])
        assert_true(type(new_property) is Property)
        assert_true(type(new_property.entity) is Entity)

        property_found = self.module.get_property(new_property.id)
        assert_true(property_found is not None)
        assert_true(type(property_found) is Property)
        assert_true(type(property_found.entity) is Entity)

        assert_equal(property_found.id, new_property.id)
        assert_equal(property_found.name, pro_name)
        assert_equal(property_found.description, pro_desc)
        assert_equal(property_found.entity.id, new_property.entity.id)
        assert_equal(property_found.entity.name, ent_name)
        assert_equal(property_found.entity.description, ent_desc)

    @log_function(logger)
    def test_26_set_value_ok(self):

        entity = self.module.get_entity(1)
        assert_true(type(entity) is Entity)

        pro_name = 'pro name'
        pro_desc = 'pro desc'
        new_property_tuple = self.module.create_property(pro_name, pro_desc, entity)
        new_property = new_property_tuple[0]
        assert_true(new_property is not None)
        assert_true(new_property_tuple[1])
        assert_true(type(new_property) is Property)
        assert_true(type(new_property.entity) is Entity)

        ins_name = 'instance name'
        new_instance_tuple = self.module.create_instance(ins_name, entity)
        new_instance = new_instance_tuple[0]
        assert_true(new_instance is not None)
        assert_true(new_instance_tuple[1])
        assert_true(type(new_instance) is Instance)
        assert_true(type(new_instance.entity) is Entity)

        value = 'new value'
        new_value_tuple = self.module.create_value(new_property, new_instance, value)
        new_value = new_value_tuple[0]
        assert_true(new_value is not None)
        assert_true(new_value_tuple[1])
        assert_true(type(new_value) is Value)
        assert_true(type(new_value.property) is Property)
        assert_true(type(new_value.instance) is Instance)

        value_found = self.module.get_value(new_value.id)
        assert_true(type(value_found) is Value)
        assert_true(type(value_found.property) is Property)
        assert_true(type(value_found.instance) is Instance)
        assert_equal(value_found.id, new_value.id)
        assert_equal(value_found.value, value)

        assert_equal(value_found.property.id, new_property.id)
        assert_equal(value_found.property.name, pro_name)
        assert_equal(value_found.property.description, pro_desc)

        assert_equal(value_found.instance.id, new_instance.id)
        assert_equal(value_found.instance.name, ins_name)

    @log_function(logger)
    def test_27_set_value_fail(self):
        entity_pro = self.module.get_entity(1)
        assert_true(type(entity_pro) is Entity)
        entity_ins = self.module.get_entity(2)
        assert_true(type(entity_ins) is Entity)

        pro_name = 'pro name fail'
        pro_desc = 'pro desc fail'
        new_property_tuple = self.module.create_property(pro_name, pro_desc, entity_pro)
        new_property = new_property_tuple[0]
        assert_true(new_property is not None)
        assert_true(new_property_tuple[1])
        assert_true(type(new_property) is Property)
        assert_true(type(new_property.entity) is Entity)

        ins_name = 'instance name fail'
        new_instance_tuple = self.module.create_instance(ins_name, entity_ins)
        new_instance = new_instance_tuple[0]
        assert_true(new_instance is not None)
        assert_true(new_instance_tuple[1])
        assert_true(type(new_instance) is Instance)
        assert_true(type(new_instance.entity) is Entity)

        value = 'new value'
        new_value_tuple = self.module.create_value(new_property, new_instance, value)
        new_value = new_value_tuple[0]
        assert_true(new_value is None)
        assert_true(new_value_tuple[1] == False)

    @log_function(logger)
    def test_28_get_user_id_ok(self):
        username = 'username si'
        password = 'password si'
        first_name = 'first name'
        family_name = 'family name'
        email = 'mail'
        roles_list = list()

        role = self.module.get_role(1)
        roles_list.append(role)

        new_user_tuple = self.module.create_user(username, password, first_name, family_name, email, roles_list)
        new_user_id = new_user_tuple[0].id

        login_user = new_user_tuple[0].username
        login_pass = new_user_tuple[0].password

        found_user_id = self.module.get_user_id(login_user, login_pass)
        assert_true(type(found_user_id) is not None)
        assert_true(type(found_user_id) is int)
        assert_equal(new_user_id, found_user_id)

    @log_function(logger)
    def test_28_get_user_id_ok(self):
        username = 'username no'
        password = 'password no'
        first_name = 'first name'
        family_name = 'family name'
        email = 'mail'
        roles_list = list()

        role = self.module.get_role(2)
        roles_list.append(role)

        new_user_tuple = self.module.create_user(username, password, first_name, family_name, email, roles_list)

        login_user = new_user_tuple[0].username + 'algo'
        login_pass = new_user_tuple[0].password + 'algo'

        found_user_id = self.module.get_user_id(login_user, login_pass)
        assert_true(found_user_id is None)
