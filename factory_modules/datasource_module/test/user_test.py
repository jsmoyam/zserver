import unittest

import common.main as server
import common

# Run the server
server.main()


class UserTestDatasourceModule(unittest.TestCase):

    @classmethod
    def setup_class(cls):
        """
        This method is run once for each class before any tests are run
        """

        # Get the database module
        UserTestDatasourceModule.module = common.module_manager.get_module('datasource_module')

    @classmethod
    def teardown_class(cls):
        """
        This method is run once for each class _after_ all tests are run
        """

    def test_1_create_user(self) -> None:
        """
        Create a new user
        """

        from factory_modules.datasource_module.models.user_model import UserCreateInputData

        user_data = UserCreateInputData(username='user_test', password='pass_test', permissions=[1, 2])

        # Create the user
        result = self.module.create(user_data)

        self.assertTrue(result)

    def test_2_get_all_user(self) -> None:
        """
        Create a new user
        """

        from factory_modules.datasource_module.models.user_model import UserRetrieveInputData

        user_data = UserRetrieveInputData(id=None)

        # Get all users
        result = self.module.retrieve(user_data)

        self.assertTrue(result)

    def test_3_update_users(self) -> None:
        """
        Create a new user
        """

        from factory_modules.datasource_module.models.user_model import UserUpdateInputData

        user_data = UserUpdateInputData(id=1, username='user_new', new_password='another_pass',
                                        permissions=[1], is_active=1)

        # Update the user
        result = self.module.update(user_data)

        self.assertTrue(result)

    def test_4_delete_user(self) -> None:
        """
        Delete a new user
        """

        from factory_modules.datasource_module.models.user_model import UserDeleteInputData

        user_data = UserDeleteInputData(id=1)

        # Delete the user
        result = self.module.delete(user_data)

        self.assertTrue(result)


if __name__ == '__main__':
    unittest.main()
