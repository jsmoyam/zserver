import os
import sqlite3

from nose.tools import assert_equal, assert_true, assert_is_none, nottest
from pandas import DataFrame

from common import config
from common.infra_modules.parsing_module.parsing_module import ParsingModule


class TestParsingModule(object):
    module = None
    test_files_parent_location = None
    database = '/tmp/test.db'


    def __init__(self):
        pass


    @classmethod
    def setup_class(cls):
        """
        This method is run once for each class before any tests are run.
        """
        TestParsingModule.module = ParsingModule(config, 'parsing_module')
        TestParsingModule.test_files_parent_location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


    @classmethod
    def teardown_class(cls):
        """
        This method is run once for each class _after_ all tests are run.
        """
        pass


    def setup(self):
        """
        This method is run once before _each_ test method is executed.
        """
        pass


    def teardown(self):
        """
        This method is run once after _each_ test method is executed.
        """
        if os.path.isfile(TestParsingModule.database):
            os.remove(TestParsingModule.database)


    def test_1_parse_csv_with_separated_commas(self) -> None:
        """
        Parse normal csv file (values separated with commas).
        """
        csv_path = os.path.join(TestParsingModule.test_files_parent_location, 'files/Sacramentorealestatetransactions_with_comma.csv')
        connection = sqlite3.connect(TestParsingModule.database)
        table = 'test_table'

        self.module.load_csv_to_database(csv_path, connection, table)

        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM {}'.format(table))

        number_of_entries = int(cursor.fetchone()[0])
        assert_equal(number_of_entries, 985)

        cursor.execute('SELECT * FROM {}'.format(table))
        number_of_columns = int(len(cursor.description))
        assert_equal(number_of_columns, 12)

        connection.close()


    def test_2_parse_csv_with_separated_semicolons(self) -> None:
        """
        Parse normal csv file with values separated with semicolons.
        """
        csv_path = os.path.join(TestParsingModule.test_files_parent_location, 'files/Sacramentorealestatetransactions_with_semicolon.csv')
        connection = sqlite3.connect(TestParsingModule.database)
        table = 'test_table'

        self.module.load_csv_to_database(csv_path, connection, table, sep=';')

        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM {}'.format(table))

        number_of_entries = int(cursor.fetchone()[0])
        assert_equal(number_of_entries, 985)

        cursor.execute('SELECT * FROM {}'.format(table))
        number_of_columns = int(len(cursor.description))
        assert_equal(number_of_columns, 12)

        connection.close()


    def test_3_parse_csv_with_separated_verticalbars(self) -> None:
        """
        Parse normal csv file with values separated with vertical bars.
        """
        csv_path = os.path.join(TestParsingModule.test_files_parent_location, 'files/Sacramentorealestatetransactions_with_verticalbar.csv')
        connection = sqlite3.connect(TestParsingModule.database)
        table = 'test_table'

        self.module.load_csv_to_database(csv_path, connection, table, sep='|')

        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM {}'.format(table))

        number_of_entries = int(cursor.fetchone()[0])
        assert_equal(number_of_entries, 985)

        cursor.execute('SELECT * FROM {}'.format(table))
        number_of_columns = int(len(cursor.description))
        assert_equal(number_of_columns, 12)

        connection.close()


    def test_4_parse_medium_size_csv_with_separated_commas(self) -> None:
        """
        Parse normal medium size csv file (values separated with commas).
        """
        csv_path = os.path.join(TestParsingModule.test_files_parent_location, 'files/FL_insurance_sample_with_comma.csv')
        connection = sqlite3.connect(TestParsingModule.database)
        table = 'test_table'

        self.module.load_csv_to_database(csv_path, connection, table)

        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM {}'.format(table))

        number_of_entries = int(cursor.fetchone()[0])
        assert_equal(number_of_entries, 36634)

        cursor.execute('SELECT * FROM {}'.format(table))
        number_of_columns = int(len(cursor.description))
        assert_equal(number_of_columns, 18)

        connection.close()


    def test_5_parse_medium_size_csv_with_separated_spaces(self) -> None:
        """
        Parse normal medium size csv file (values separated with spaces).
        """
        csv_path = os.path.join(TestParsingModule.test_files_parent_location, 'files/FL_insurance_sample_with_spaces.csv')
        connection = sqlite3.connect(TestParsingModule.database)
        table = 'test_table'

        self.module.load_csv_to_database(csv_path, connection, table, sep=' ')

        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM {}'.format(table))

        number_of_entries = int(cursor.fetchone()[0])
        assert_equal(number_of_entries, 36634)

        cursor.execute('SELECT * FROM {}'.format(table))
        number_of_columns = int(len(cursor.description))
        assert_equal(number_of_columns, 18)

        connection.close()


    def test_6_load_csv_into_dataframe_with_header(self) -> None:
        """
        Parse normal csv file without header and values separated with circumflexes.
        """
        csv_path = os.path.join(TestParsingModule.test_files_parent_location, 'files/Sacramentorealestatetransactions_with_comma.csv')

        dataframe = self.module.load_csv(csv_path)

        assert_equal(type(dataframe), DataFrame)

        number_of_entries = len(dataframe)
        assert_equal(number_of_entries, 985)

        number_of_columns = len(dataframe.columns.values)
        assert_equal(number_of_columns, 12)


    def test_7(self):
        csv_path = os.path.join(TestParsingModule.test_files_parent_location, 'files/FL_insurance_sample_with_spaces_without_header.csv')
        header = 'policyID statecode county eq_site_limit hu_site_limit fl_site_limit fr_site_limit tiv_2011 tiv_2012 eq_site_deductible hu_site_deductible fl_site_deductible fr_site_deductible point_latitude point_longitude line construction point_granularity'
        self.module.insert_header_to_csv(csv_path, header)

        connection = sqlite3.connect(TestParsingModule.database)
        table = 'test_table'

        self.module.load_csv_to_database(csv_path, connection, table, sep=' ')

        self.module.remove_firstline_from_csv(csv_path)

        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM {}'.format(table))

        number_of_entries = int(cursor.fetchone()[0])
        assert_equal(number_of_entries, 36634)

        cursor.execute('SELECT * FROM {}'.format(table))
        number_of_columns = int(len(cursor.description))
        assert_equal(number_of_columns, 18)

        connection.close()


    def test_8(self):
        csv_path = os.path.join(TestParsingModule.test_files_parent_location, 'files/FL_insurance_sample_with_spaces_without_header.csv')
        header = 'policyID statecode county eq_site_limit hu_site_limit fl_site_limit fr_site_limit tiv_2011 tiv_2012 eq_site_deductible hu_site_deductible fl_site_deductible fr_site_deductible point_latitude point_longitude line construction point_granularity'

        connection = sqlite3.connect(TestParsingModule.database)
        table = 'test_table'

        self.module.load_csv_to_database(csv_path, connection, table, header=header, sep=' ')

        cursor = connection.cursor()
        cursor.execute('SELECT COUNT(*) FROM {}'.format(table))

        number_of_entries = int(cursor.fetchone()[0])
        assert_equal(number_of_entries, 36634)

        cursor.execute('SELECT * FROM {}'.format(table))
        number_of_columns = int(len(cursor.description))
        assert_equal(number_of_columns, 18)

        connection.close()
