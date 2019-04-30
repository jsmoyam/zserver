import pandas as pd

from common import config
from common.infra_modules.infra_module import InfraModule
from common.infra_modules.parsing_module import MODULE_NAME


logger = config.get_log(MODULE_NAME)


class ParsingModule(InfraModule):

    def initialize(self) -> None:
        """
        This method create and initialize all variables and resources needed.
        :return: None.
        """

        self.load_config_parameters()


    def load_config_parameters(self) -> None:
        """
        Load configuration parameters of the module from configuration file.
        """
        pass


    def insert_header_to_csv(self, file_path:str, header: str, old_sep=',', header_sep=',') -> bool:
        has_header = True

        with open(file_path, 'r+') as file:
            first_line = file.readline().rstrip('\n')

            if first_line != header:
                header = header.replace(old_sep, header_sep)
                has_header = False
                file.seek(0, 0)
                content = file.read()
                file.seek(0, 0)
                file.write(header + '\n' + content)

        return has_header


    def remove_firstline_from_csv(self, file_path:str) -> None:
        with open(file_path, 'r') as fin:
            data = fin.read().splitlines(True)
        with open(file_path, 'w') as fout:
            fout.writelines(data[1:])


    def load_csv(self, file_path:str, header=None, sep=',') -> pd.DataFrame:
        has_header = False

        if header:
            has_header = self.insert_header_to_csv(file_path, header)

        dataframe = pd.read_csv(file_path, sep=sep)

        if has_header:
            self.remove_firstline_from_csv(file_path)

        return dataframe


    def load_csv_to_database(self, file_path:str, connection, table:str, header=None, sep=' ', skiprows=None) -> None:
        has_header = True

        if header:
            has_header = self.insert_header_to_csv(file_path, header)

        # for chunk in pd.read_csv(file_path, sep=sep, chunksize=1000):
        #     chunk.to_sql(name=table, con=connection, if_exists='append', index=False)

        dataframe = pd.read_csv(file_path, sep=sep, skiprows=skiprows)
        dataframe.to_sql(name=table, con=connection, if_exists='append', index=False, chunksize=1000)

        if header and not has_header:
            self.remove_firstline_from_csv(file_path)

        return has_header


    def load_xlsx(self, file_path:str, xlsx_cols=None) -> pd.DataFrame:
        dataframe = pd.read_excel(file_path, parse_cols=xlsx_cols)

        return dataframe


    def load_xlsx_to_database(self, xlsx_dataframe: pd.DataFrame, connection, table:str, if_exists='append') -> None:
        xlsx_dataframe.to_sql(name=table, con=connection, if_exists=if_exists, index=False, chunksize=1000)
