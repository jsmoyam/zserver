import logging
from common.module import ViewModule, authenticate
from sky_modules.datasource_module import MODULE_NAME
from sky_modules.datasource_module.model_datasource_module import PermissionSchema, RolesSchema, UsersSchema, \
    TypesSchema, StatusSchema, CasesSchema, RoleInputData, RoleInputDataSchema, UserInputData, \
    UserInputDataSchema, CaseTypeInputData, CaseTypeInputDataSchema, CaseStatusInputData, CaseStatusInputDataSchema, \
    CaseInputData, CaseInputDataSchema, EvidencesSchema, EvidenceInputData, EvidenceInputDataSchema, UploadsSchema, \
    UploadInputData, UploadInputDataSchema, FilesSchema, FileInputData, FileInputDataSchema, EntitiesSchema, \
    EntityInputData, EntityInputDataSchema, InstancesSchema, InstanceInputData, InstanceInputDataSchema, \
    PropertiesSchema, PropertyInputData, PropertyInputDataSchema, ValuesSchema, ValueInputData, ValueInputDataSchema
from common.app_model import DataResult, AppException, GenericErrorMessages
logger = logging.getLogger(MODULE_NAME)

@authenticate()
class DatasourceModuleView(ViewModule):

    def get_all_permissions(self):
        try:
            list_permission = self.app_module.get_all_permissions()
            code = 'CODE_OK'
            msg = 'All permissions list'
        except AppException as e:
            list_permission = list()
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, PermissionSchema, list_permission, code, msg=msg)
            return result

    def get_permission(self, permission_id):
        try:
            permission = self.app_module.get_permission(permission_id)
            if permission is None:
                code = 'CODE_NOT_FOUND'
                msg = 'Permission ' + permission_id + ' not found'
            else:
                code = 'CODE_OK'
                msg = 'Permission ' + permission_id + ' found'
        except AppException as e:
            permission = None
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, PermissionSchema, permission, code, msg=msg)
            return result

    def get_all_roles(self):
        try:
            roles = self.app_module.get_all_roles()
            code = 'CODE_OK'
            msg = 'All roles list'
        except AppException as e:
            roles = list()
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, RolesSchema, roles, code, msg=msg)
            return result

    def get_role(self, role_id):
        try:
            role = self.app_module.get_role(role_id)
            if role is None:
                code = 'CODE_NOT_FOUND'
                msg = 'Role ' + role_id + ' not found'
            else:
                code = 'CODE_OK'
                msg = 'Role ' + role_id + ' found'
        except AppException as e:
            role = None
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, RolesSchema, role, code, msg=msg)
            return result

    def get_all_users(self):
        try:
            users = self.app_module.get_all_users()
            code = 'CODE_OK'
            msg = 'All users list'
        except AppException as e:
            users = list()
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, UsersSchema, users, code, msg=msg)
            return result

    def get_user(self, user_id):
        try:
            user = self.app_module.get_user(user_id)
            if user is None:
                code = 'CODE_NOT_FOUND'
                msg = 'User ' + user_id + ' not found'
            else:
                code = 'CODE_OK'
                msg = 'User ' + user_id + ' found'
        except AppException as e:
            user = None
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, UsersSchema, user, code, msg=msg)
            return result

    def get_user_id(self, username, password):
        try:
            user = self.app_module.get_user_id(username, password)
            if user is None:
                return None
            else:
                return user.id
        except AppException as e:
            return None

    def get_all_case_types(self):
        try:
            types = self.app_module.get_all_case_types()
            code = 'CODE_OK'
            msg = 'All case types list'
        except AppException as e:
            types = list()
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, TypesSchema, types, code, msg=msg)
            return result

    def get_case_type(self, type_id):
        try:
            type = self.app_module.get_case_type(type_id)
            if type is None:
                code = 'CODE_NOT_FOUND'
                msg = 'Case type ' + type_id + ' not found'
            else:
                code = 'CODE_OK'
                msg = 'Case type ' + type_id + ' found'
        except AppException as e:
            type = None
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, TypesSchema, type, code, msg=msg)
            return result

    def get_all_case_status(self):
        try:
            status_list = self.app_module.get_all_case_status()
            code = 'CODE_OK'
            msg = 'All case status list'
        except AppException as e:
            status_list = list()
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, StatusSchema, status_list, code, msg=msg)
            return result

    def get_case_status(self, status_id):
        try:
            status = self.app_module.get_case_status(status_id)
            if status is None:
                code = 'CODE_NOT_FOUND'
                msg = 'Case status ' + status_id + ' not found'
            else:
                code = 'CODE_OK'
                msg = 'Case status ' + status_id + ' found'
        except AppException as e:
            status = None
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, StatusSchema, status, code, msg=msg)
            return result

    def get_all_cases(self):
        try:
            cases = self.app_module.get_all_cases()
            code = 'CODE_OK'
            msg = 'All cases list'
        except AppException as e:
            cases = list()
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, CasesSchema, cases, code, msg=msg)
            return result

    def get_case(self, case_id):
        try:
            case = self.app_module.get_case(case_id)
            if case is None:
                code = 'CODE_NOT_FOUND'
                msg = 'Case ' + case_id + ' not found'
            else:
                code = 'CODE_OK'
                msg = 'Case ' + case_id + ' found'
        except AppException as e:
            case = None
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, CasesSchema, case, code, msg=msg)
            return result

    def get_all_evidences(self):
        try:
            evidences = self.app_module.get_all_evidences()
            code = 'CODE_OK'
            msg = 'All evidences list'
        except AppException as e:
            evidences = list()
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, EvidencesSchema, evidences, code, msg=msg)
            return result

    def get_evidence(self, evidence_id):
        try:
            evidence = self.app_module.get_evidence(evidence_id)
            if evidence is None:
                code = 'CODE_NOT_FOUND'
                msg = 'Evidence ' + evidence_id + ' not found'
            else:
                code = 'CODE_OK'
                msg = 'Evidence ' + evidence_id + ' found'
        except AppException as e:
            evidence = None
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, EvidencesSchema, evidence, code, msg=msg)
            return result

    def get_all_uploads(self, evidence_id):
        try:
            upload_list = self.app_module.get_all_uploads(evidence_id)
            code = 'CODE_OK'
            msg = 'All uploads list for evidence ' + evidence_id
        except AppException as e:
            upload_list = list()
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, UploadsSchema, upload_list, code, msg=msg)
            return result

    def get_upload(self, upload_id):
        try:
            upload = self.app_module.get_upload(upload_id)
            if upload is None:
                code = 'CODE_NOT_FOUND'
                msg = 'Upload ' + upload_id + ' not found'
            else:
                code = 'CODE_OK'
                msg = 'Upload ' + upload_id + ' found'
        except AppException as e:
            upload = None
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, UploadsSchema, upload, code, msg=msg)
            return result

    def get_all_files(self, upload_id):
        try:
            files_list = self.app_module.get_all_files(upload_id)
            code = 'CODE_OK'
            msg = 'All files list for upload ' + upload_id
        except AppException as e:
            files_list = list()
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, FilesSchema, files_list, code, msg=msg)
            return result

    def get_file(self, file_id):
        try:
            file = self.app_module.get_file(file_id)
            if file is None:
                code = 'CODE_NOT_FOUND'
                msg = 'File ' + file_id + ' not found'
            else:
                code = 'CODE_OK'
                msg = 'File ' + file_id + ' found'
        except AppException as e:
            file = None
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, FilesSchema, file, code, msg=msg)
            return result

    def get_all_entities(self):
        try:
            entities_list = self.app_module.get_all_entities()
            code = 'CODE_OK'
            msg = 'All entities list'
        except AppException as e:
            entities_list = list()
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, EntitiesSchema, entities_list, code, msg=msg)
            return result

    def get_entity(self, entity_id):
        try:
            entity = self.app_module.get_entity(entity_id)
            if entity is None:
                code = 'CODE_NOT_FOUND'
                msg = 'Entity ' + entity_id + ' not found'
            else:
                code = 'CODE_OK'
                msg = 'Entity ' + entity_id + ' found'
        except AppException as e:
            entity = None
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, EntitiesSchema, entity, code, msg=msg)
            return result

    def get_all_instances(self, entity_id):
        try:
            instance_list = self.app_module.get_all_instances(entity_id)
            code = 'CODE_OK'
            msg = 'All instances list for entity ' + entity_id
        except AppException as e:
            instance_list = list()
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, InstancesSchema, instance_list, code, msg=msg)
            return result

    def get_instance(self, instance_id):
        try:
            instance = self.app_module.get_instance(instance_id)
            if instance is None:
                code = 'CODE_NOT_FOUND'
                msg = 'Instance ' + instance_id + ' not found'
            else:
                code = 'CODE_OK'
                msg = 'Instance ' + instance_id + ' found'
        except AppException as e:
            instance = None
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, InstancesSchema, instance, code, msg=msg)
            return result

    def get_all_properties(self, entity_id):
        try:
            property_list = self.app_module.get_all_properties(entity_id)
            code = 'CODE_OK'
            msg = 'All properties list for entity ' + entity_id
        except AppException as e:
            property_list = list()
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, PropertiesSchema, property_list, code, msg=msg)
            return result

    def get_property(self, property_id):
        try:
            property = self.app_module.get_property(property_id)
            if property is None:
                code = 'CODE_NOT_FOUND'
                msg = 'Property ' + property_id + ' not found'
            else:
                code = 'CODE_OK'
                msg = 'Property ' + property_id + ' found'
        except AppException as e:
            property = None
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, PropertiesSchema, property, code, msg=msg)
            return result

    def get_all_values(self, instance_id):
        try:
            value_list = self.app_module.get_all_values(instance_id)
            code = 'CODE_OK'
            msg = 'All values list for instance ' + instance_id
        except AppException as e:
            value_list = list()
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, ValuesSchema, value_list, code, msg=msg)
            return result

    def get_value(self, value_id):
        try:
            value = self.app_module.get_value(value_id)
            if value is None:
                code = 'CODE_NOT_FOUND'
                msg = 'Value ' + value_id + ' not found'
            else:
                code = 'CODE_OK'
                msg = 'Value ' + value_id + ' found'
        except AppException as e:
            value = None
            code = 'CODE_ERROR'
            msg = str(e)
        finally:
            result = self.app_module.create_output(DataResult, ValuesSchema, value, code, msg=msg)
            return result


class CreateRoleModuleView(ViewModule):

    # AMJ.  OJO!!!! este método no está probado
    def post(self):
        # For testing:  curl -d '{"name": "url_name1", "description": "url_des_1", "permissions": [{"description": "init_pppp1", "id": 1, "name": "p1"}, {"description": "init_pppp2", "id": 2, "name": "p2"}]}' -H "Content-type: application/json" -X POST http://localhost:5000/ds/createrole/
        input_data = self.app_module.create_input(RoleInputData, RoleInputDataSchema)

        role, success = self.app_module.create_role(input_data.name, input_data.description, input_data.permissions)

        if success is True:
            code = 'CODE_CREATED_OK'
            msg = 'Role created (' + role.id + ')'
        else:
            code = 'CODE_CREATED_ERROR'
            msg = 'Role not created (' + GenericErrorMessages.DATABASE_ERROR + ')'

        result = self.app_module.create_output(DataResult, RolesSchema, role, code, msg=msg)
        return result


class CreateUserModuleView(ViewModule):

    # AMJ.  OJO!!!! este método no está probado (la llamada desde la vista)
    def post(self):
        # For testing: curl -d '{"username": "url_user", "password": "url_password", "first_name": "url_first", "family_name": "url_fam", "email": "url_email", "roles": [{"description": "init_des", "id": 1, "name": "init_name", "permissions": [{"description": "init_pppp1", "id": 1, "name": "p1"}, {"description": "init_pppp2", "id": 2, "name": "p2"}]}] }' -H "Content-type: application/json" -X POST http://localhost:5000/ds/createuser/
        input_data = self.app_module.create_input(UserInputData, UserInputDataSchema)

        user, success = self.app_module.create_user(input_data.username, input_data.password, input_data.first_name,
                                                    input_data.family_name, input_data.email, input_data.roles)

        if success is True:
            code = 'CODE_CREATED_OK'
            msg = 'User created (' + user.id + ')'
        else:
            code = 'CODE_CREATED_ERROR'
            msg = 'User not created (' + GenericErrorMessages.DATABASE_ERROR + ')'

        result = self.app_module.create_output(DataResult, UsersSchema, user, code, msg=msg)
        return result


class CreateCaseTypeModuleView(ViewModule):

    # AMJ.  OJO!!!! este método no está probado (la llamada desde la vista)
    def post(self):
        # For testing: curl -d '{"name": "url case type name 1", "description": "url case type descrp 1"}' -H "Content-type: application/json" -X POST http://localhost:5000/ds/createcasetype/
        input_data = self.app_module.create_input(CaseTypeInputData, CaseTypeInputDataSchema)

        type, success = self.app_module.create_case_type(input_data.name, input_data.description)

        if success is True:
            code = 'CODE_CREATED_OK'
            msg = 'Case type created (' + type.id + ')'
        else:
            code = 'CODE_CREATED_ERROR'
            msg = 'Case type not created (' + GenericErrorMessages.DATABASE_ERROR + ')'

        result = self.app_module.create_output(DataResult, TypesSchema, type, code, msg=msg)
        return result


class CreateCaseStatusModuleView(ViewModule):

    # AMJ.  OJO!!!! este método no está probado (la llamada desde la vista)
    def post(self):
        # For testing: curl -d '{"name": "url case status name 1", "description": "url case status descrp 1"}' -H "Content-type: application/json" -X POST http://localhost:5000/ds/createcasestatus/
        input_data = self.app_module.create_input(CaseStatusInputData, CaseStatusInputDataSchema)

        status, success = self.app_module.create_case_status(input_data.name, input_data.description)

        if success is True:
            code = 'CODE_CREATED_OK'
            msg = 'Case status created (' + status.id + ')'
        else:
            code = 'CODE_CREATED_ERROR'
            msg = 'Case status not created (' + GenericErrorMessages.DATABASE_ERROR + ')'

        result = self.app_module.create_output(DataResult, StatusSchema, status, code, msg=msg)
        return result


class CreateCaseModuleView(ViewModule):

    # AMJ.  OJO!!!! este método no está probado (la llamada desde la vista)
    def post(self):
        # For testing: curl -d '{"formal_name": "url formal1", "friend_name": "url friend1", "creation_datetime": "2018-09-07T17:34:24.301054+00:00", "num_win": 101, "num_lin": 102, "num_ios": 103, "num_mal": 104, "num_pac": 105, "num_log": 106, "case_status": {"description": "status descrp 1", "id": 1, "name": "cstatus 1"}, "case_type": {"description": "case descrp 2", "id": 2, "name": "ctype 2"}}' -H "Content-type: application/json" -X POST http://localhost:5000/ds/createcase/
        input_data = self.app_module.create_input(CaseInputData, CaseInputDataSchema)

        case, success = self.app_module.create_case(input_data.formal_name, input_data.friend_name,
                                                    input_data.creation_datetime, input_data.num_win,
                                                    input_data.num_lin, input_data.num_ios,
                                                    input_data.num_mal, input_data.num_pac, input_data.num_log,
                                                    input_data.case_type,
                                                    input_data.case_status)

        if success is True:
            code = 'CODE_CREATED_OK'
            msg = 'Case created (' + case.id + ')'
        else:
            code = 'CODE_CREATED_ERROR'
            msg = 'Case not created (' + GenericErrorMessages.DATABASE_ERROR + ')'

        result = self.app_module.create_output(DataResult, CasesSchema, case, code, msg=msg)
        return result


class CreateEvidenceModuleView(ViewModule):

    # AMJ.  OJO!!!! este método no está probado (la llamada desde la vista)
    def post(self):
        # For testing: curl -d '{"alias": "url alias 1", "size": "234.78", "owner":{"email": "ini_email2", "family_name": "ini_fam2", "first_name": "ini_first2", "id": 2, "roles": [{"description": "init_des", "id": 1, "name": "init_name", "permissions": [{"description": "init_pppp1", "id": 1, "name": "p1"}, {"description": "init_pppp2", "id": 2, "name": "p2"}]}, {"description": "desc_role 2", "id": 2, "name": "role2", "permissions": [{"description": "init_pppp2", "id": 2, "name": "p2"}, {"description": "init_pppp3", "id": 3, "name": "p3"}]}], "username": "ini_user2", "password": "ini_password2"}}' -H "Content-type: application/json" -X POST http://localhost:5000/ds/createevidence/
        input_data = self.app_module.create_input(EvidenceInputData, EvidenceInputDataSchema)

        evidence, success = self.app_module.create_evidence(input_data.alias, input_data.size, input_data.owner)

        if success is True:
            code = 'CODE_CREATED_OK'
            msg = 'Evidence created (' + evidence.id + ')'
        else:
            code = 'CODE_CREATED_ERROR'
            msg = 'Evidence not created (' + GenericErrorMessages.DATABASE_ERROR + ')'

        result = self.app_module.create_output(DataResult, EvidencesSchema, evidence, code, msg=msg)
        return result


class CreateUploadModuleView(ViewModule):

    # AMJ.  OJO!!!! este método no está probado (la llamada desde la vista)
    def post(self):
        # For testing: curl -d '{"path": "curl path 1", "size" : "1004.02", "type": "url type 1", "evidence": {"alias": "url alias 1", "size": "234.78", "owner":{"email": "ini_email2", "family_name": "ini_fam2", "first_name": "ini_first2", "id": 2, "roles": [{"description": "init_des", "id": 1, "name": "init_name", "permissions": [{"description": "init_pppp1", "id": 1, "name": "p1"}, {"description": "init_pppp2", "id": 2, "name": "p2"}]}, {"description": "desc_role 2", "id": 2, "name": "role2", "permissions": [{"description": "init_pppp2", "id": 2, "name": "p2"}, {"description": "init_pppp3", "id": 3, "name": "p3"}]}], "username": "ini_user2", "password": "ini_password2"}}}' -H "Content-type: application/json" -X POST http://localhost:5000/ds/createupload/
        input_data = self.app_module.create_input(UploadInputData, UploadInputDataSchema)

        upload, success = self.app_module.create_upload(input_data.path, input_data.size, input_data.type,
                                                        input_data.evidence)

        if success is True:
            code = 'CODE_CREATED_OK'
            msg = 'Upload created (' + upload.id + ')'
        else:
            code = 'CODE_CREATED_ERROR'
            msg = 'Upload not created (' + GenericErrorMessages.DATABASE_ERROR + ')'

        result = self.app_module.create_output(DataResult, UploadsSchema, upload, code, msg=msg)
        return result


class CreateFileModuleView(ViewModule):

    # AMJ.  OJO!!!! este método no está probado (la llamada desde la vista)
    def post(self):
        # For testing: curl -d '{"path": "url path 1", "size": "123.45", "name": "url name 1", "hash_md5": "url hash_md5 1", "hash_sha256": "ulr hash_sha256 1", "upload": {"path": "curl path 1", "size" : "1004.02", "type": "url type 1", "evidence": {"alias": "url alias 1", "size": "234.78", "owner":{"email": "ini_email2", "family_name": "ini_fam2", "first_name": "ini_first2", "id": 2, "roles": [{"description": "init_des", "id": 1, "name": "init_name", "permissions": [{"description": "init_pppp1", "id": 1, "name": "p1"}, {"description": "init_pppp2", "id": 2, "name": "p2"}]}, {"description": "desc_role 2", "id": 2, "name": "role2", "permissions": [{"description": "init_pppp2", "id": 2, "name": "p2"}, {"description": "init_pppp3", "id": 3, "name": "p3"}]}], "username": "ini_user2", "password": "ini_password2"}}}}' -H "Content-type: application/json" -X POST http://localhost:5000/ds/createfile/
        input_data = self.app_module.create_input(FileInputData, FileInputDataSchema)

        file, success = self.app_module.create_upload(input_data.path, input_data.size, input_data.name,
                                                      input_data.hash_md5, input_data.hash_sha256, input_data.upload)

        if success is True:
            code = 'CODE_CREATED_OK'
            msg = 'File created (' + file.id + ')'
        else:
            code = 'CODE_CREATED_ERROR'
            msg = 'File not created (' + GenericErrorMessages.DATABASE_ERROR + ')'

        result = self.app_module.create_output(DataResult, FilesSchema, file, code, msg=msg)
        return result


class CreateEntityModuleView(ViewModule):

    # AMJ.  OJO!!!! este método no está probado
    def post(self):

        # For testing: curl -d '{"name": "url name 1", "description": "url description 1"}' -H "Content-type: application/json" -X POST http://localhost:5000/ds/createentity/
        input_data = self.app_module.create_input(EntityInputData, EntityInputDataSchema)

        entity, success = self.app_module.create_entity(input_data.name, input_data.description)

        if success is True:
            code = 'CODE_CREATED_OK'
            msg = 'Entity created (' + entity.id + ')'
        else:
            code = 'CODE_CREATED_ERROR'
            msg = 'Entity not created (' + GenericErrorMessages.DATABASE_ERROR + ')'

        result = self.app_module.create_output(DataResult, EntitiesSchema, entity, code, msg=msg)
        return result


class CreateInstanceModuleView(ViewModule):

    # AMJ.  OJO!!!! este método no está probado
    def post(self):

        # For testing: # For testing: curl -d '{"name" : "url instance name ", "entity": {"description": "ent desc 2", "id": 2, "name": "ent name 2"}}' -H "Content-type: application/json" -X POST http://localhost:5000/ds/createinstance/
        input_data = self.app_module.create_input(InstanceInputData, InstanceInputDataSchema)

        instance, success = self.app_module.create_instance(input_data.name, input_data.entity)

        if success is True:
            code = 'CODE_CREATED_OK'
            msg = 'Instance created (' + instance.id + ')'
        else:
            code = 'CODE_CREATED_ERROR'
            msg = 'Instance not created (' + GenericErrorMessages.DATABASE_ERROR + ')'

        result = self.app_module.create_output(DataResult, InstancesSchema, instance, code, msg=msg)
        return result


class CreatePropertyModuleView(ViewModule):

    # AMJ.  OJO!!!! este método no está probado
    def post(self):

        # For testing: curl -d '{"name": "url property name 1", "description": "url property  desc 1", "entity": {"description": "ent desc 1", "id": 1, "name": "ent name 1"}}' -H "Content-type: application/json" -X POST http://localhost:5000/ds/createproperty/
        input_data = self.app_module.create_input(PropertyInputData, PropertyInputDataSchema)

        property, success = self.app_module.create_property(input_data.name, input_data.description, input_data.entity)

        if success is True:
            code = 'CODE_CREATED_OK'
            msg = 'Property created (' + property.id + ')'
        else:
            code = 'CODE_CREATED_ERROR'
            msg = 'Property not created (' + GenericErrorMessages.DATABASE_ERROR + ')'

        result = self.app_module.create_output(DataResult, PropertiesSchema, property, code, msg=msg)
        return result


class CreateValueModuleView(ViewModule):

    # AMJ.  OJO!!!! este método no está probado
    def post(self):

        # For testing:
        input_data = self.app_module.create_input(ValueInputData, ValueInputDataSchema)

        value, success = self.app_module.create_value(input_data.property, input_data.instance, input_data.value)

        if success is True:
            code = 'CODE_CREATED_OK'
            msg = 'Value created (' + value.id + ')'
        else:
            code = 'CODE_CREATED_ERROR'
            msg = 'Value not created (' + GenericErrorMessages.DATABASE_ERROR + ')'

        result = self.app_module.create_output(DataResult, ValuesSchema, value, code, msg=msg)
        return result

