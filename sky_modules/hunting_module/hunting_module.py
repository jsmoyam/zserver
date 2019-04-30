import os
import fabric, re
import datetime
import sqlite3
import time
from datetime import datetime, date, timedelta
import subprocess
import csv

from common import config, module_manager
from sky_modules.hunting_module import MODULE_NAME
# from sky_modules.hunting_module.execute_channel_task import ExecuteChannelTask
from sky_modules.sky_module import SkyModule
from sky_modules.hunting_module.load_hunting_database import HuntingDatabase as hd
from sky_modules.hunting_module.views_hunting_module import HuntingModuleChannelView, HuntingModuleHostView, \
    HuntingModuleHistoricalCsvView, HuntingModuleEvidenceOutputsView, HuntingModuleReportView, HuntingModuleManualView
from sky_modules.hunting_module.execute_cmd_task import ExecuteCmdTask

from common import config
from common.infra_tools.task_thread import TaskThread
from common.infra_modules.database_module.database_module import DatabaseModule
from common.infra_modules.parsing_module.parsing_module import ParsingModule
from common.infra_modules.system_commands_module.system_commands_module import SystemCommandsModule

logger = config.get_log(MODULE_NAME)


class HuntingModule(SkyModule):
    parsing_module = None
    database_module = None
    database = None
    hosts_table = 'host'
    host_channel = 'channel_name'
    historical_host = 'historical_host'
    agent_status_folder = ''

    def initialize(self):
        """
        This method create and initialize all variables and resources needed
        :return: None
        """
        HuntingModule.parsing_module = module_manager.get_module('parsing_module')
        # self.database_module = module_manager.get_module('database_module')
        HuntingModule.database_module = module_manager.get_module('database_module')
        HuntingModule.system_commands_module = module_manager.get_module('system_commands_module')

        self.load_config_parameters()
        self.create_database_tables_if_not_exist()

        self.register_url(HuntingModuleChannelView, '/hunting/channel')
        self.register_url(HuntingModuleHostView, '/hunting/host')
        self.register_url(HuntingModuleHistoricalCsvView, '/hunting/historical')
        self.register_url(HuntingModuleEvidenceOutputsView, '/hunting/evidence_outputs')
        self.register_url(HuntingModuleReportView, '/hunting/report')
        self.register_url(HuntingModuleManualView, '/hunting/session/manual')

        self.execute_channel = self.ExecuteChannelTask(HuntingModule.database_module, HuntingModule.parsing_module)
        self.execute_channel.set_interval(HuntingModule.execute_channel_task_interval)
        self.execute_channel.start()

        self.agent_task = self.AgentStatusTask(HuntingModule.database_module, HuntingModule.system_commands_module)
        self.agent_task.set_interval(HuntingModule.agent_status_task_interval)
        # self.agent_task.start()

        if not os.path.isdir(HuntingModule.hunting_results_dir):
            os.makedirs(HuntingModule.hunting_results_dir)

    def load_config_parameters(self) -> None:
        """
        Load configuration parameters of the module from configuration file.
        """
        HuntingModule.database_for_panda = self.module_config.get_value(MODULE_NAME, 'connection_database')
        HuntingModule.sql_script = self.module_config.get_value(MODULE_NAME, 'sql_script')
        HuntingModule.csv_headers = dict({
            'hosts': self.module_config.get_value(MODULE_NAME, 'csv_hosts_header'),
            'ps': self.module_config.get_value(MODULE_NAME, 'csv_ps_header'),
            'evos': self.module_config.get_value(MODULE_NAME, 'csv_evos_header'),
            'hits': self.module_config.get_value(MODULE_NAME, 'csv_hits_header')
        })
        HuntingModule.xlsx_header = self.module_config.get_value(MODULE_NAME, 'xlsx_columns')
        HuntingModule.task_interval = int(self.module_config.get_value(MODULE_NAME, 'task_interval'))
        # Config for ExecuteChannelTask
        HuntingModule.execute_channel_task_interval = int(
            self.module_config.get_value(MODULE_NAME, 'execute_channel_task_interval'))
        HuntingModule.hunting_script_notif_path = self.module_config.get_value(MODULE_NAME, 'hunting_script_notif_path')
        HuntingModule.hunting_script_path = self.module_config.get_value(MODULE_NAME, 'hunting_script_path')
        HuntingModule.hunting_results_dir = self.module_config.get_value(MODULE_NAME, 'hunting_results_dir')
        HuntingModule.hosts_filename = self.module_config.get_value(MODULE_NAME, 'hosts_filename')
        # Config for AgentStatusTask
        HuntingModule.agent_status_folder = self.module_config.get_value(MODULE_NAME, 'agent_status_folder')
        HuntingModule.agent_status_task_interval = int(
            self.module_config.get_value(MODULE_NAME, 'agent_status_task_interval'))

        HuntingModule.all_host_file = self.module_config.get_value(MODULE_NAME, 'all_host_file')
        HuntingModule.cancel_session_script = self.module_config.get_value(MODULE_NAME, 'cancel_session_script')

    def load_hosts_xlsx(self, xlsx_params) -> bool:
        full_path = xlsx_params.get('full_path')
        xlsx_header = xlsx_params.get('xlsx_header', None)
        xlsx_country = xlsx_params.get('country', None)

        loaded = False
        connection = sqlite3.connect(HuntingModule.database_for_panda)
        hosts_columns = HuntingModule.csv_headers.get('hosts').split()
        if xlsx_header is None:
            xlsx_columns = list(csv.reader([HuntingModule.xlsx_header], delimiter=' '))[0]
        else:
            xlsx_columns = list(csv.reader([xlsx_header], delimiter=' '))[0]

        try:
            if os.path.isfile(full_path):
                (current_number_of_hosts, current_number_of_channels) = self.get_number_of_channels_and_hosts()

                xlsx_dataframe = HuntingModule.parsing_module.load_xlsx(full_path, xlsx_cols=xlsx_columns)

                new_cols = dict()
                for idx, val in enumerate(xlsx_columns):
                    new_cols[val] = hosts_columns[idx]

                xlsx_dataframe.rename(columns=new_cols,
                                      inplace=True)

                xlsx_dataframe.dropna(subset=['ip'], inplace=True)
                xlsx_dataframe.drop_duplicates(subset=['ip'], inplace=True)

                xlsx_hostnames = list(xlsx_dataframe['ip'])
                existing_hostnames_query = 'SELECT ip FROM host WHERE country="{}" AND ip IN ("{}")'.format(
                    xlsx_country, '","'.join(map(str, xlsx_hostnames)))
                result = HuntingModule.database_module.exec_query(existing_hostnames_query)
                ips = [value['ip'] for value in result]

                indexNames = xlsx_dataframe[xlsx_dataframe['ip'].apply(self.check_valid_ip)].index
                xlsx_dataframe.drop(indexNames, inplace=True)

                indexNames = xlsx_dataframe[xlsx_dataframe['ip'].isin(ips)].index
                to_insert = xlsx_dataframe.drop(indexNames, inplace=False)

                indexNames = xlsx_dataframe[~xlsx_dataframe['ip'].isin(ips)].index
                to_update = xlsx_dataframe.drop(indexNames, inplace=False)

                date_creation = self.get_datetime_in_hunting_database_format()
                HuntingModule.parsing_module.load_xlsx_to_database(to_insert, connection, self.hosts_table)
                self.update_hosts_dates_and_empty_channels(date_creation, country=xlsx_country)

                query = 'DROP TABLE IF EXISTS host_aux'
                HuntingModule.database_module.exec_query(query)

                query = 'CREATE TABLE IF NOT EXISTS host_aux(id INTEGER NOT NULL PRIMARY KEY,hostname TEXT DEFAULT "",ip TEXT NOT NULL,operating_system TEXT DEFAULT "",date_creation INTEGER DEFAULT 0,agent_available INTEGER DEFAULT 0,forest_available INTEGER DEFAULT 0,channel_name TEXT DEFAULT "unknown",country TEXT DEFAULT "",managed_by TEXT DEFAULT "")'
                HuntingModule.database_module.exec_query(query)

                HuntingModule.parsing_module.load_xlsx_to_database(to_update, connection,
                                                                   '{}_aux'.format(self.hosts_table))
                query = 'UPDATE {} SET channel_name="unknown" WHERE date_creation=0 AND channel_name IS NULL'.format(
                    '{}_aux'.format(self.hosts_table))
                HuntingModule.database_module.exec_query(query)

                query = 'UPDATE host SET ' \
                        '  hostname = (SELECT host_aux.hostname FROM host_aux WHERE host_aux.ip = host.ip), ' \
                        '  channel_name = (SELECT host_aux.channel_name FROM host_aux WHERE host_aux.ip = host.ip), ' \
                        '  operating_system = (SELECT host_aux.operating_system FROM host_aux WHERE host_aux.ip = host.ip AND host_aux.country = host.country ) ' \
                        'WHERE EXISTS (SELECT * FROM host_aux WHERE host_aux.ip = host.ip)'
                HuntingModule.database_module.exec_query(query)

                self.insert_new_host_channels()

                loaded = True

                (new_number_of_hosts, new_number_of_channels) = self.get_number_of_channels_and_hosts()

                total_hosts = new_number_of_hosts - current_number_of_hosts
                total_channels = new_number_of_channels - current_number_of_channels
                self.insert_historical_xlsx(full_path, total_channels, total_hosts)

                new_host_notify = self.get_hosts_by_creation_date(date_creation)
                for host in new_host_notify:
                    # Call to Forest
                    cmd = HuntingModule.hunting_script_notif_path + " -ip=" + host['ip'] + " -host=" + host['hostname']

                    p = subprocess.Popen("exec " + cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                         stdin=subprocess.PIPE)

                    codes = {
                        'HOST_NO_ACCESIBLE': [0, 0],
                        'HOST_REGISTERED': [1, 1],
                        'HOST_EXISTS_IN_CASE': [1, 1],
                        'DEFAULT': [0, 0]
                    }

                    out, err = p.communicate()

                    code_output = out.decode('utf-8').split('\n')[-2]

                    query = 'UPDATE host SET agent_available={}, forest_available={} WHERE id={}'.format(
                        codes.get(code_output, codes['DEFAULT'])[0], codes.get(code_output, codes['DEFAULT'])[1],
                        host['id'])
                    HuntingModule.database_module.exec_query(query)

                    with open(HuntingModule.all_host_file, 'a') as all_host_file:
                        all_host_file.write(
                            '{},{},{},{},{}\n'.format(host['hostname'], host['ip'], host['operating_system'],
                                                      host['channel_name'], host['managed_by']))


        except Exception as e:
            print(e)

        return loaded

    def check_valid_ip(self, ip):
        return not re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", ip)

    def load_hunting_info_from_files(self, task_info) -> (bool, bool):
        return self.execute_channel.load_hunting_info_from_files(task_info)

    def get_host_data(self) -> bool:
        query = 'SELECT * FROM {}'.format(HuntingModule.hosts_table)

        return HuntingModule.database_module.exec_query(query)

    def get_hosts_by_creation_date(self, date_creation):
        hosts = HuntingModule.database_module.exec_query(
            'SELECT * FROM host WHERE date_creation="{}"'.format(date_creation))
        return hosts

    def update_hosts_channel(self, old_channel: str, new_channel: str) -> None:
        datetime_modified = self.get_datetime_in_hunting_database_format()

        # Save to historical host table
        query = 'INSERT INTO "{}" (ip, country, old_channel_name, date_modified, status) ' \
                'SELECT ip, country, channe_name, "{}", "{}" FROM host)'.format(self.historical_host, datetime_modified,
                                                                                "CHANGE_CHANNEL")
        HuntingModule.database_module.exec_query(query)

        # Update channel from all hosts
        query = 'UPDATE {} SET channel_name="{}", date_modified={} WHERE channel_name="{}"'.format(self.hosts_table,
                                                                                                   new_channel,
                                                                                                   datetime_modified,
                                                                                                   old_channel)

        HuntingModule.database_module.exec_query(query)
        self.insert_new_host_channels()

    def create_database_tables_if_not_exist(self) -> None:
        hd.create_hunting_database(HuntingModule.database_for_panda, HuntingModule.sql_script)

    def remove_repeated_hosts(self) -> None:
        query = 'DELETE FROM host WHERE (id NOT IN (SELECT MIN(id) FROM host GROUP BY hostname)) OR ip IS NULL'

        HuntingModule.database_module.exec_query(query)

    def update_hosts_dates_and_empty_channels(self, date_creation, country=None) -> None:
        query = 'UPDATE host SET channel_name="unknown" WHERE date_creation=0 AND channel_name IS NULL'
        HuntingModule.database_module.exec_query(query)

        if country:
            query = 'UPDATE host SET country="{}" WHERE date_creation=0 and country=""'.format(country)
            HuntingModule.database_module.exec_query(query)

        query = 'UPDATE host SET date_creation={}, date_modified={} WHERE date_creation=0'.format(date_creation,
                                                                                                  date_creation)

        HuntingModule.database_module.exec_query(query)

    def insert_new_host_channels(self) -> None:
        query = 'SELECT DISTINCT(channel_name) FROM host WHERE channel_name IS NOT NULL AND channel_name NOT IN (SELECT DISTINCT(name) FROM channel)'

        result = HuntingModule.database_module.exec_query(query)

        for channel in result:
            self.add_empty_channel(channel['channel_name'])

    def get_number_of_channels_and_hosts(self) -> (int, int):
        query = 'SELECT COUNT(hostname) AS number_of_hosts, COUNT(DISTINCT(channel_name)) AS number_of_channels FROM host'

        result = HuntingModule.database_module.exec_query(query)

        return (int(result[0]['number_of_hosts']), int(result[0]['number_of_channels']))

    def get_channel(self, name):
        """
        Retrieve a single channel from database, by its name.
        :param name: The name of the channel to retrieve.
        :return: A dict containing the information of the channel.
        """
        result = HuntingModule.database_module.exec_query('SELECT * FROM channel WHERE name="{}"'.format(name))
        return result

    @staticmethod
    def get_all_channels():
        """
        Retrieve all the channels in database
        :return: a list of dictionaries. Each dict is a row in database.
        """
        result = HuntingModule.database_module.exec_query('SELECT * FROM channel')
        return result

    def get_channels(self):
        """
        Retrieve all the channels in database
        :return: a list of dictionaries. Each dict is a row in database.
        """
        result = HuntingModule.database_module.exec_query('SELECT name FROM channel')
        return result

    def add_channel(self, input_data):
        """
        Insert a new channel in database.
        :param input_data: dict with the information of the new channel.
        :return:
        """
        result = HuntingModule.database_module.exec_query(
            'INSERT INTO channel VALUES ("{}","{}","{}","{}","{}","{}","{}")'.format(input_data['name'],
                                                                                     input_data['hunting_type'],
                                                                                     input_data['gevo_associated'],
                                                                                     input_data['concurrence_type'],
                                                                                     input_data['concurrence_time'],
                                                                                     input_data['scheduling'],
                                                                                     input_data['priority']))

        return result

    def add_empty_channel(self, channel_name):
        result = HuntingModule.database_module.exec_query(
            'INSERT INTO channel (name) VALUES ("{}")'.format(channel_name))

        return result

    def update_channel(self, input_data):
        """
        Update a channel in database.
        :param input_data: dict with the new information about the channel.
        :return:
        """
        result = HuntingModule.database_module.exec_query('UPDATE channel SET hunting_type="{}", gevo_associated="{}",'
                                                          'concurrence_type="{}", concurrence_time="{}", scheduling="{}", priority="{}" WHERE name="{}"'.format(
            input_data['hunting_type'],
            input_data['gevo_associated'],
            input_data['concurrence_type'],
            input_data['concurrence_time'],
            input_data['scheduling'],
            input_data['priority'],
            input_data['name']))

        return result

    def delete_channel(self, name):
        """
        Delete a channel in database, idetified by its name.
        :param name: Name of the channel to delete
        :return:
        """
        result = HuntingModule.database_module.exec_query('DELETE FROM channel WHERE name="{}"'.format(name))
        return result

    def get_historical_xlsx(self):
        """
        Get all the rows in the table historical_xlsx
        :return: A list of dictionaries. Each dict represents a row.
        """
        result = HuntingModule.database_module.exec_query('SELECT * FROM historical_xlsx')
        return result

    def insert_historical_xlsx(self, full_path, total_channels, total_hosts):
        """
        Insert a new row in table historical_xlsx with the info given in the parameters.
        :param full_path: full path of the xlsx file.
        :param total_channels: total channels in the xlsx file.
        :param total_hosts: total hosts in the xlsx file.
        :return: True if the insert is done, False otherwise.
        """
        current_datetime = self.get_datetime_in_hunting_database_format()
        data = {'full_path': full_path,
                'total_channels': total_channels,
                'total_hosts': total_hosts,
                'date': current_datetime}
        result = HuntingModule.database_module.insert('historical_xlsx', data)
        return result

    def get_datetime_in_hunting_database_format(self, date=None) -> int:
        if date:
            current_date = date
        else:
            current_date = datetime.now()

        return int(current_date.strftime("%Y%m%d%H%M%S"))

    def get_report_total(self):
        """
        Retrieve a single channel from database, by its name.
        :return: A dict containing the information of the channel.
        """
        result = dict()

        total_scope = HuntingModule.database_module.exec_query(
            'SELECT COUNT(*) AS total_scope FROM host')[0]
        result.update(total_scope)
        total_agent_up = HuntingModule.database_module.exec_query(
            'SELECT COUNT(*) AS total_agents_up FROM host WHERE agent_available=1 AND active=1')[0]
        result.update(total_agent_up)
        total_agents_down = HuntingModule.database_module.exec_query(
            'SELECT COUNT(*) AS total_agents_down FROM host WHERE agent_available=0 AND active=1')[0]
        result.update(total_agents_down)
        total_availables_hosts = HuntingModule.database_module.exec_query(
            'SELECT COUNT(*) AS total_availables_hosts FROM host WHERE agent_available=1 AND forest_available=1 AND active=1')[
            0]
        result.update(total_availables_hosts)
        total_finished_hosts = HuntingModule.database_module.exec_query(
            'SELECT COUNT(*) AS total_finished_hosts FROM processed_host')[
            0]
        result.update(total_finished_hosts)
        total_session_hosts = HuntingModule.database_module.exec_query(
            'SELECT COUNT(DISTINCT(id)) AS total_session_hosts FROM host WHERE active=1 AND id IN (SELECT id_host FROM hist_session_host)')[
            0]
        diff = int(total_session_hosts['total_session_hosts']) - int(total_finished_hosts['total_finished_hosts'])
        total_failed_hosts = {"total_failed_hosts": diff}
        result.update(total_failed_hosts)
        last_hit = HuntingModule.database_module.exec_query(
            'SELECT date AS last_hit FROM session_hit ORDER BY date DESC LIMIT 1')
        last_hit_result = last_hit[0] if len(last_hit) > 0 else {'last_hit': 0}
        result.update(last_hit_result)

        # Calculate the current progress
        if total_finished_hosts['total_finished_hosts'] > 0:
            current_progress = float(total_finished_hosts['total_finished_hosts']) / float(
                total_scope['total_scope']) * 100
            current_progress = str(round(current_progress, 2)) + "%"
        else:
            current_progress = "0%"
        result.update({'current_progress': current_progress})

        # Calculate the last day progress
        now = datetime.now()
        current_time = int(now.strftime("%Y%m%d000000"))
        total_finished_hosts_last_day = HuntingModule.database_module.exec_query(
            'SELECT COUNT(DISTINCT(id)) AS total_finished_hosts_last_day FROM host WHERE active=1 AND id IN (SELECT id_host FROM session_host WHERE status="OK" AND date_finish < {})'.format(
                current_time))[
            0]
        if total_finished_hosts_last_day['total_finished_hosts_last_day'] > 0:
            total_finished_hosts = total_finished_hosts['total_finished_hosts'] - total_finished_hosts_last_day[
                'total_finished_hosts_last_day']
            last_day_progress = float(total_finished_hosts) / float(total_scope['total_scope']) * 100
            last_day_progress = str(round(last_day_progress, 2)) + "%"
        else:
            last_day_progress = "0%"
        result.update({'last_day_progress': last_day_progress})

        last_update = HuntingModule.database_module.exec_query(
            'SELECT date_finish  AS last_update FROM session ORDER BY date_finish DESC LIMIT 1')[0]
        result.update(last_update)

        result_list = list()
        result_list.append(result)

        return result_list

    def get_report_total_by_channel(self):
        """
        Retrieve a report by channel.
        :return: A dict containing the report of the channel.
        """
        channels_list = HuntingModule.database_module.exec_query('SELECT name from channel')

        result_total = list()
        for channel in channels_list:
            if channel['name'] == 'manual':
                continue
            result = dict()

            total_scope = HuntingModule.database_module.exec_query(
                'SELECT COUNT(*) AS total_scope FROM host WHERE channel_name="{}"'.format(
                    channel['name']))[0]
            result.update(total_scope)
            total_availables_hosts = HuntingModule.database_module.exec_query(
                'SELECT COUNT(*) AS total_availables_hosts FROM host WHERE agent_available=1 AND forest_available=1 AND active=1 AND channel_name="{}"'.format(
                    channel['name']))[
                0]
            result.update(total_availables_hosts)
            total_finished_hosts = HuntingModule.database_module.exec_query(
                'SELECT COUNT(DISTINCT(id)) AS total_finished_hosts FROM host WHERE active=1 AND channel_name="{}" AND id IN (SELECT id_host FROM session_host WHERE status="OK")'.format(
                    channel['name']))[
                0]
            result.update(total_finished_hosts)
            total_session_hosts = HuntingModule.database_module.exec_query(
                'SELECT COUNT(DISTINCT(id)) AS total_session_hosts FROM host WHERE active=1 AND channel_name="{}" AND id IN (SELECT id_host FROM session_host)'.format(
                    channel['name']))[
                0]
            diff = int(total_session_hosts['total_session_hosts']) - int(total_finished_hosts['total_finished_hosts'])
            total_failed_hosts = {'total_failed_hosts': diff}
            result.update(total_failed_hosts)
            total_finished_evos = HuntingModule.database_module.exec_query(
                'SELECT COUNT(DISTINCT(evo)) AS total_finished_evos FROM (SELECT * FROM session_evo WHERE status="OK" AND id_session IN ('
                'SELECT DISTINCT(id) FROM session WHERE channel_name="{}") GROUP BY session_hostname, evo)'.format(
                    channel['name']))[
                0]
            result.update(total_finished_evos)
            total_evos_skipped = HuntingModule.database_module.exec_query(
                'SELECT COUNT(DISTINCT(evo)) AS total_evos_skipped FROM (SELECT * FROM session_evo WHERE status="SKIP" AND id_session IN ('
                'SELECT DISTINCT(id) FROM session WHERE channel_name="{}") GROUP BY session_hostname, evo)'.format(
                    channel['name']))[
                0]
            result.update(total_evos_skipped)
            total_evos = HuntingModule.database_module.exec_query(
                'SELECT COUNT(DISTINCT(evo)) AS total_evos FROM (SELECT * FROM session_evo WHERE id_session IN ('
                'SELECT DISTINCT(id) FROM session WHERE channel_name="{}") GROUP BY session_hostname, evo)'.format(
                    channel['name']))[
                0]
            result.update(total_evos)
            total_agent_up = HuntingModule.database_module.exec_query(
                'SELECT COUNT(*) AS total_agents_up FROM host WHERE agent_available=1 AND active=1 AND channel_name ="{}"'.format(channel['name']))[0]
            result.update(total_agent_up)
            total_agents_down = HuntingModule.database_module.exec_query(
                'SELECT COUNT(*) AS total_agents_down FROM host WHERE agent_available=0 AND active=1 AND channel_name ="{}"'.format(channel['name']))[0]
            result.update(total_agents_down)
            last_update = HuntingModule.database_module.exec_query(
                'SELECT date_finish AS last_update FROM session WHERE channel_name ="{}" ORDER BY date_finish DESC LIMIT 1'.format(
                    channel['name']))[
                0]
            result.update(last_update)

            # Add the channel name
            result.update({'channel_name': channel['name']})

            result_total.append(result)
        return result_total

    def get_report_details_by_channel(self, channel_name):
        """
        Retrieve a detailed report by channel.
        :return: A dict containing the detailed report of the channel.
        """
        hosts_channel = HuntingModule.database_module.exec_query('SELECT * from host WHERE channel_name="{}"'.format(channel_name))

        result_total = list()
        for host in hosts_channel:
            result = dict()

            is_processed = HuntingModule.database_module.exec_query(
                'SELECT COUNT(*) AS total from session_host WHERE id_host={} AND status="OK"'.format(host['id']))[0]
            processed = "PROCESSED" if is_processed['total'] > 0 else "NOT_PROCESSED"

            result.update({'hostname': host['hostname']})
            result.update({'ip': host['ip']})
            result.update({'processed': processed})

            result_total.append(result)

        return result_total

    def get_report_evos_details_by_channel(self, channel_name):
        """
        Retrieve a detailed report by channel.
        :return: A dict containing the detailed report of the channel.
        """
        result = HuntingModule.database_module.exec_query(
            'SELECT DISTINCT(evo) AS failed_evo, session_hostname AS hostname FROM session_evo WHERE status!="OK" '
            'AND id_session IN (SELECT DISTINCT(id) FROM session WHERE channel_name="{}") '
            'AND evo NOT IN (SELECT DISTINCT(evo) FROM session_evo WHERE status="OK") '
            'GROUP BY evo, session_hostname'.format(channel_name))

        return result

    def get_report_hits(self):
        """
        Retrieve all hits from database.
        :return: A dict containing the list of hits with information.
        """
        result = HuntingModule.database_module.exec_query('SELECT * FROM session_hits')
        return result

    def get_report_agents_status(self, status):
        """
        Retrieve all agents' status of hosts.
        :return: A dict containing the agents' status
        """
        if status != 'total':
            status = 1 if status == 'up' else 0
            hosts_agents_status = HuntingModule.database_module.exec_query(
                'SELECT hostname, ip, agent_available FROM host WHERE active = 1 AND agent_available={}'.format(status))
        else:
            hosts_agents_status = HuntingModule.database_module.exec_query(
                'SELECT hostname, ip, agent_available FROM host WHERE active = 1')

        for host in hosts_agents_status:
            if host['agent_available'] == 1:
                host['agent_available'] = 'UP'
            else:
                host['agent_available'] = 'DOWN'


        return hosts_agents_status

    def get_report_session_working(self):
        """
        Retrieve all hunting sessions working.
        :return: A dict containing the list of hunting sessions working
        """
        running_sessions = HuntingModule.database_module.exec_query('SELECT * FROM session WHERE status = "working"')

        result = list()
        for session in running_sessions:
            if float(session['total_evos']) > 0:
                current_progress = float(session['current_evos']) / float(session['total_evos']) * 100
                current_progress = str(round(current_progress, 2)) + "%"
            else:
                current_progress = "0%"

            result_dict = {
                'id_session': session['id'],
                'channel': session['channel_name'],
                'total_evos': session['total_evos'],
                'current_evos': session['current_evos'],
                'current_hits': session['current_hits'],
                'progress': current_progress
            }

            result.append(result_dict)

        return result

    def get_yesterday_report_by_channel(self):
        """
        Retrieve a yesterday report by channel.
        :return: A dict containing the report of the channel.
        """
        channels_list = HuntingModule.database_module.exec_query('SELECT name from channel')

        result_total = list()
        for channel in channels_list:
            if channel['name'] == 'manual':
                continue
            result = dict()

            today = datetime.now()
            date_start_today = int(today.strftime("%Y%m%d000000"))
            yesterday = date.today() - timedelta(1)
            date_start_yesterday = int(yesterday.strftime("%Y%m%d000000"))

            hunts = HuntingModule.database_module.exec_query(
                'SELECT COUNT(*) AS hunts FROM session WHERE channel_name="{}" AND (date_finish BETWEEN {} AND {})'.format(
                    channel['name'], date_start_yesterday, date_start_today))[0]
            result.update(hunts)

            hosts = HuntingModule.database_module.exec_query(
                'SELECT COUNT(DISTINCT(id)) AS hosts FROM host WHERE active=1 AND channel_name="{}" AND id IN ('
                'SELECT DISTINCT(id_host) FROM session_host WHERE (date_finish BETWEEN {} AND {})'
                ')'.format(
                    channel['name'], date_start_yesterday, date_start_today))[0]
            result.update(hosts)

            hits = HuntingModule.database_module.exec_query(
                'SELECT COUNT(*) AS hits FROM session_hit WHERE (date BETWEEN {} AND {}) AND session_host IN ('
                'SELECT DISTINCT(LOWER(hostname)) FROM host WHERE active=1 AND channel_name="{}")'.format(
                    date_start_yesterday, date_start_today, channel['name']))[0]
            result.update(hits)

            # Add the channel name
            result.update({'channel_name': channel['name']})

            result_total.append(result)

        return result_total

    def get_history_report(self):
        """
        Retrieve a yesterday report by channel.
        :return: A dict containing the report of the channel.
        """
        result_total = list()

        # Get the date of the first session
        first_session = HuntingModule.database_module.exec_query('SELECT date_start from session WHERE date_start > 0 ORDER BY date_start ASC LIMIT 1')

        if len(first_session) > 0:
            format_str = '%Y%m%d%H%M%S'
            first_date_ms = first_session[0]['date_start']
            date_start = datetime.strptime(str(first_date_ms), format_str).date()
            date_finish = datetime.now().date()

            channels_list = HuntingModule.database_module.exec_query('SELECT name from channel')

            first_date = 0
            for dt in self.dates_between_range_from_dates(date_start, date_finish):
                result = dict()

                first_date = dt if first_date == 0 else first_date

                for channel in channels_list:
                    if channel['name'] == 'manual':
                        continue
                    total_finished_hosts = HuntingModule.database_module.exec_query(
                        'SELECT COUNT(DISTINCT(id)) AS total_finished_hosts FROM host WHERE active=1 AND channel_name="{}" AND id IN (SELECT id_host FROM session_host WHERE status="OK" AND date_start > {} AND date_finish <= {})'.format(
                            channel['name'], int(first_date.strftime("%Y%m%d000000")), int(dt.strftime("%Y%m%d235959"))))[
                        0]

                    if total_finished_hosts['total_finished_hosts'] > 0:
                        total_hosts = HuntingModule.database_module.exec_query(
                            'SELECT COUNT(*) AS total_hosts FROM host WHERE channel_name="{}"'.format(
                                channel['name']))[
                            0]

                        total_hosts = total_hosts['total_hosts']
                        progress = round(total_finished_hosts['total_finished_hosts'] / total_hosts * 100, 2)
                    else:
                        progress = 0

                    str_key = 'hosts_channel_' + channel['name']
                    str_value = '{} ({}%)'.format(total_finished_hosts['total_finished_hosts'], progress)
                    result.update({str_key: str_value})

                result.update({'date': dt.strftime('%Y%m%d')})

                result_total.append(result)

        return result_total

    def dates_between_range_from_dates(self, date_start, date_finish):
        for n in range(int((date_finish - date_start).days) + 1):
            yield date_start + timedelta(n)


    def execute_manual_hunting(self, data):

        now = self.get_datetime_in_hunting_database_format()
        channel_name = 'manual'
        base_name = 'hunting'

        logger.info('[EXECUTE_MANUAL_TASK] Starting manual hunting execution.')

        # Create the folder for the evos and hits files
        folder_name = '{}-{}-{}'.format(base_name, channel_name, now)
        full_path = os.path.join(HuntingModule.hunting_results_dir, folder_name)
        try:
            os.mkdir(full_path)
        except Exception as err:
            print(err)
            return False

        # Insert task in database.
        data_task = {'channel_name': channel_name,
                     'status': self.ExecuteChannelTask.STATUS_WORKING,
                     'forest_path': full_path,
                     }

        # Create a session for this manual hunting.
        result = HuntingModule.database_module.insert('session', data_task)
        id_session = HuntingModule.database_module.exec_query(
            'SELECT id FROM session WHERE forest_path="{}"'.format(full_path))[0]['id']

        logger.info('[EXECUTE_MANUAL_TASK] Inserted manual session with id: {}'.format(id_session))

        # Insert a row for each manual host.
        for host in data['hosts_list']:

            host_db = HuntingModule.database_module.exec_query(
                'SELECT * FROM host where ip="{}" and hostname="{}" and country="{}"'.format(
                    host['ip'], host['hostname'], data['country']
                ))

            # Check the status of the host.
            code = 'HOST_NOT_FOUND'
            id_host = -1
            if len(host_db) != 0:
                id_host = host_db[0]['id']
                if host_db[0]['active'] == 0:
                    code = 'HOST_NOT_ACTIVE'
                elif host_db[0]['forest_available'] == 0 or host_db[0]['agent_available'] == 0:
                    code = 'HOST_NOT_AVAILABLE'
                else:
                    code = 'HOST_OK'

            HuntingModule.database_module.exec_query(
                'INSERT INTO manual_hunting (id_host, hostname, ip, country, channel_name, code, id_session)'
                'values ({},"{}","{}","{}","{}","{}",{})'.format(id_host, host['hostname'], host['ip'],
                                                                 data['country'], channel_name, code, id_session))

        hosts_availables = HuntingModule.database_module.exec_query(
            'SELECT * FROM manual_hunting where id_session={} and code="{}"'.format(id_session, 'HOST_OK'))
        logger.info('[EXECUTE_MANUAL_TASK] {} hosts availables for manual hunting session with id: {}'.format(
            len(hosts_availables), id_session))

        # Insert in hostfile all the available host
        with open(os.path.join(full_path, HuntingModule.hosts_filename), 'w') as f:
            for host in hosts_availables:
                new_line = "{} {}\n".format(host['hostname'], host['ip'])
                f.write(new_line)
                query = 'INSERT INTO session_host (id_session, id_host) VALUES (' \
                        '(SELECT id FROM session WHERE forest_path="{}"), ' \
                        '(SELECT id FROM host WHERE country="{}" AND ip="{}"))' \
                    .format(full_path, host['country'], host['ip'])
                HuntingModule.database_module.exec_query(query)

        # Save info for hosts not availables

        hosts_not_availables = HuntingModule.database_module.exec_query(
            'SELECT * FROM manual_hunting where id_session={} and code="{}"'.format(id_session, 'HOST_NOT_AVAILABLE'))
        logger.info('[EXECUTE_MANUAL_TASK] {} hosts not availables for manual hunting session with id: {}'.format(
            len(hosts_not_availables), id_session))

        for host in hosts_not_availables:
            query = 'INSERT INTO session_host (id_session, id_host, status) VALUES (' \
                    '(SELECT id FROM session WHERE forest_path="{}"), ' \
                    '(SELECT id FROM host WHERE country="{}" AND ip="{}"), ' \
                    '"NOT_AVAILABLE")' \
                .format(full_path, host['country'], host['ip'])
            HuntingModule.database_module.exec_query(query)

        # Call to EvidenceProcessor
        cmd = HuntingModule.hunting_script_path + " -path=" + folder_name + " -priority=medium"

        logger.info('[EXECUTE_MANUAL_TASK] Running thread to execute manual hunting on channel')
        command = 'exec {}'.format(cmd)
        t = ExecuteCmdTask(logger, command)
        t.set_only_one_execution()
        t.start()

        logger.info('[EXECUTE_MANUAL_TASK] Executed thread on manual hunting')

        result = {'processed_hosts': list(), 'unavailable_hosts': list(), 'inactive_hosts': list(),
                  'not_found_hosts': list()}
        session_hosts = HuntingModule.database_module.exec_query(
            'SELECT * FROM manual_hunting where id_session={}'.format(id_session))

        for host in session_hosts:
            host_info = {'hostname': host['hostname'], 'ip': host['ip']}
            if host['code'] == 'HOST_OK':
                result['processed_hosts'].append(host_info)
            elif host['code'] == 'HOST_NOT_ACTIVE':
                result['inactive_hosts'].append(host_info)
            elif host['code'] == 'HOST_NOT_FOUND':
                result['not_found_hosts'].append(host_info)
            else:
                result['unavailable_hosts'].append(host_info)

        result.update({'result': True})
        return result

    def execute_manual_channel(self, channel_name, times):

        valid_channels = HuntingModule.database_module.exec_query('SELECT name FROM channel')

        if any(channel['name'] == channel_name for channel in valid_channels):
            is_channel_working = self.execute_channel.is_channel_working(channel_name)

            if not is_channel_working:
                # Update the channel
                concurrence_time = int(times)
                concurrence_type = "by_times" if concurrence_time > 0 else 'continuous'
                result = HuntingModule.database_module.exec_query(
                    'UPDATE channel SET concurrence_type="{}", concurrence_time="{}", scheduling="{}" WHERE name="{}"'.format(
                        concurrence_type,
                        concurrence_time,
                        0,
                        channel_name))

                # Execute the task
                channel = \
                HuntingModule.database_module.exec_query('SELECT * FROM channel WHERE name="{}"'.format(channel_name))[
                    0]
                self.execute_channel.launch_task(channel)

                # Set the result
                return {'success': 'true', 'msg': 'INIT_EXECUTION'}

            else:
                return {'success': 'false', 'msg': 'CHANNEL_IS_WORKING'}

        return {'success': 'false', 'msg': 'NOT_VALID_CHANNEL'}

    def stop_manual_channel(self, channel_name):

        valid_channels = HuntingModule.database_module.exec_query('SELECT name FROM channel')

        for channel in valid_channels:
            if channel['name'] == channel_name:
                try:
                    # Update the channel
                    HuntingModule.database_module.exec_query(
                        'UPDATE channel SET scheduling="{}" WHERE name="{}"'.format(-1, channel_name))

                    working_sessions = HuntingModule.database_module.exec_query('SELECT * FROM session WHERE channel_name="{}" and status="{}"'.format(
                        channel_name, self.execute_channel.STATUS_WORKING))
                    if len(working_sessions) > 0:
                        for session in working_sessions:

                            cmd = HuntingModule.cancel_session_script + " -path=" + session['forest_path']
                            p = subprocess.Popen("exec " + cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                 stdin=subprocess.PIPE)
                            out, err = p.communicate()

                    # Set the result
                    return {'success': 'true', 'msg': 'CHANNEL_STOPPED'}
                except Exception as err:
                    print(err)
                    return {'success': 'false', 'msg': 'INTERNAL_ERROR'}

        return {'success': 'false', 'msg': 'NOT_VALID_CHANNEL'}

    class ExecuteChannelTask(TaskThread):

        # Constants for database values

        STATUS_WORKING = "working"
        STATUS_FINISHED = "finished"
        STATUS_FAILED = "failed"
        CONCURRENCE_CONTINUOUS = "continuous"
        CONCURRENCE_BY_DATE = "by_date"
        CONCURRENCE_BY_TIMES = "by_times"

        def __init__(self, db: DatabaseModule, ps: ParsingModule) -> None:
            TaskThread.__init__(self)
            self.db = db
            self.ps = ps

        def is_channel_active(self, channel) -> bool:
            """
            Check if channel is active in database
            :param channel: dict with the channel data
            :return: bool
            """

            now = int(datetime.now().strftime("%Y%m%d%H%M%S"))
            result = False
            # Check if the channel is on scheduling date.
            if not self.is_channel_working(channel['name']):
                if channel['scheduling'] != -1 and channel['scheduling'] < now:

                    # Check if the channel is continuous, executed to date or executed n times.
                    if channel['concurrence_type'] == __class__.CONCURRENCE_CONTINUOUS:
                        # If it's continuous, channel is active
                        result = True
                    elif channel['concurrence_type'] == __class__.CONCURRENCE_BY_DATE \
                            and int(channel['concurrence_time']) > now:
                        # If it's executed until date, and date has not been passed, channel is active.
                        result = True
                    elif channel['concurrence_type'] == __class__.CONCURRENCE_BY_TIMES:
                        # If it's executed by number of times, and it's has not been executed the max number of times,
                        # channel is active.
                        times_executed = self.db.exec_query(
                            'SELECT COUNT(*) FROM session WHERE channel_name="{}"'.format(channel['name']))
                        if times_executed[0]['COUNT(*)'] < int(channel['concurrence_time']):
                            result = True

            return result

        def is_channel_working(self, channel_name: int) -> bool:
            """
            Check if channel is processing in forest
            :return: bool
            """

            row = self.db.exec_query(
                'SELECT status FROM session WHERE channel_name="{}" ORDER BY id DESC'.format(channel_name)) # Quizás hay que cogerlas todas y ver si alguna está en working.
            if len(row) > 0 and row[0]['status'] == __class__.STATUS_WORKING:
                return True
            else:
                return False

        def get_all_channels(self) -> list:

            """
            Get all channels from database
            :return: a list with all channels
            """
            rows = self.db.exec_query('SELECT * FROM channel')
            return rows

        def get_working_channels(self) -> list:
            """
            Get all processing channels
            :return: list of working channels
            """
            channels = self.db.exec_query(
                'SELECT * FROM channel WHERE name in (SELECT channel_name FROM session WHERE status="{}")'.format(
                    __class__.STATUS_WORKING))
            return channels

        def update_task_channel_status(self, channel_name: str, status: str) -> None:

            """
            Update channel status in task table
            :param channel_name: channel name
            :param status: new status
            :return: None
            """
            result = self.db.exec_query(
                'UPDATE session SET status="{}" WHERE channel_name="{}"'.format(status, channel_name))

        def get_hosts_from_channel(self, channel_name):
            hosts = self.db.exec_query('SELECT * FROM host WHERE channel_name="{}" AND active = 1'.format(channel_name))
            return hosts

        def get_hosts_available_from_channel(self, channel_name):

            failed_hosts = self.get_hosts_not_executed_from_channel(channel_name)
            success_hosts = self.get_ok_hosts(channel_name, failed_hosts)

            result = failed_hosts + success_hosts
            return result

        def get_ok_hosts(self, channel_name, failed_hosts):
            hosts = self.db.exec_query(
                'SELECT * FROM host WHERE channel_name="{}" AND agent_available = 1 AND forest_available = 1 AND active=1'.format(
                    channel_name))
            result = list()
            for host in hosts:
                if host not in failed_hosts:
                    result.append(host)
            return result

        def get_hosts_not_executed_from_channel(self, channel_name):
            """
            Return the host (from the given channel) than has been never processed.
            :param channel_name: The name of the channel to get the hosts.
            :return: A list with the host not processed.
            """
            hunting_type = HuntingModule.database_module.exec_query('SELECT hunting_type FROM channel WHERE'
                                                                    ' name="{}"'.format(channel_name))[0]['hunting_type']
            processed_hosts = HuntingModule.database_module.exec_query('SELECT * FROM processed_host WHERE hunting_type="{}"'
                                                                       .format(hunting_type))
            channel_hosts = HuntingModule.database_module.exec_query('SELECT * FROM host WHERE channel_name="{}" AND '
                                                                     'agent_available = 1 AND forest_available = 1 AND active=1'
                                                                     .format(channel_name))
            not_executed = list()
            for c_host in channel_hosts:
                found = False
                for p_host in processed_hosts:
                    if c_host['id'] == p_host['id_host']:
                        found = True
                        break
                if not found:
                    not_executed.append(c_host)

            not_executed = [host for host in channel_hosts if host not in processed_hosts]

            return not_executed

        def get_hosts_not_availables_from_channel(self, channel_name):
            hosts = self.db.exec_query(
                'SELECT * FROM host WHERE channel_name="{}" AND (agent_available = 0 OR forest_available = 0)'.format(
                    channel_name))
            return hosts

        def execute_command(self, command: str, sudo=False, host='localhost', user=None, password=None, port=None):
            """
            Execute shell command in local or remote server
            :param sudo: True/False, execute as sudo
            :param host: host in which execute command
            :param user: ssh username
            :param password: ssh password
            :param port: ssh port
            :return: stdout and stderr in tuple, (None, None) if error
            """

            regexp = '^localhost$|^127(?:\.[0-9]+){0,2}\.[0-9]+$|^(?:0*\:)*?:?0*1$'
            is_localhost = bool(re.search(regexp, host))

            # Create fabric connection
            try:
                if is_localhost:
                    conn = fabric.Connection(host)
                    modified_command = 'sudo ' + command if sudo else command
                    output = conn.local(modified_command)
                else:
                    conn = fabric.Connection(host, user=user, port=port)
                    if password and len(password) > 0:
                        conn.connect_kwargs.look_for_keys = False
                        conn.connect_kwargs.password = password
                        conn.connect_kwargs.allow_agent = False
                    output = conn.sudo(command) if sudo else conn.run(command)

                return output.stdout, output.stderr
            except Exception:
                print('Error ejecutando')
                return None, None

        def launch_task(self, channel) -> bool:
            """
            Launch task to evidence processor
            :param channel: channel to launch
            :return: None
            """
            base_name = 'hunting'

            # Create the folder for the evos and hits files

            db_date = datetime.now().strftime("%Y%m%d%H%M%S")
            folder_name = '{}-{}-{}'.format(base_name, channel['name'], db_date)
            full_path = os.path.join(HuntingModule.hunting_results_dir, folder_name)

            try:
                os.mkdir(full_path)
            except Exception as err:
                print(err)
                return False

            # Insert task in database
            data = {'channel_name': channel['name'],
                    'status': __class__.STATUS_WORKING,
                    'forest_path': full_path,
                    }
            result = HuntingModule.database_module.insert('session', data)

            # Get all the hosts availables and write them to a file
            if channel['force_execution'] == 0:
                hosts_availables = self.get_hosts_not_executed_from_channel(channel['name'])
            else:
                hosts_availables = self.get_hosts_available_from_channel(channel['name'])

            with open(os.path.join(full_path, HuntingModule.hosts_filename), 'w') as f:
                for host in hosts_availables:
                    new_line = "{} {}\n".format(host['hostname'], host['ip'])
                    f.write(new_line)
                    query = 'INSERT INTO session_host (id_session, id_host) VALUES (' \
                            '(SELECT id FROM session WHERE forest_path="{}"), ' \
                            '(SELECT id FROM host WHERE country="{}" AND ip="{}"))' \
                        .format(full_path, host['country'], host['ip'])
                    self.db.exec_query(query)

            # Save info for hosts not availables
            if channel['force_execution'] == 1:
                hosts_not_availables = self.get_hosts_not_availables_from_channel(channel['name'])
                for host in hosts_not_availables:
                    query = 'INSERT INTO session_host (id_session, id_host, status) VALUES (' \
                            '(SELECT id FROM session WHERE forest_path="{}"), ' \
                            '(SELECT id FROM host WHERE country="{}" AND ip="{}"), ' \
                            '"NOT_AVAILABLE")' \
                        .format(full_path, host['country'], host['ip'])
                    self.db.exec_query(query)

            # Call to EvidenceProcessor
            cmd = HuntingModule.hunting_script_path + " -path=" + folder_name + " -priority=" + channel['priority']

            logger.info(
                '[EXECUTE_CHANNEL_TASK] Running thread to execute hunting on channel {}'.format(channel['name']))
            command = 'exec {}'.format(cmd)
            t = ExecuteCmdTask(logger, command)
            t.set_only_one_execution()
            t.start()

            logger.info('[EXECUTE_CHANNEL_TASK] Executed thread on channel {}'.format(channel['name']))
            return True




        def add_processed_host(self, id_host, hunting_type, host_status):
            """
            Add a processed host if it has not been inserted yet.
            :param id_host:
            :param hunting_type:
            :return: None
            """
            result = HuntingModule.database_module.exec_query('SELECT * FROM processed_host WHERE id_host={} and '
                                                              'hunting_type="{}"'.format(id_host, hunting_type))
            if len(result) == 0:
                HuntingModule.database_module.exec_query('INSERT INTO processed_host (id_host, hunting_type, status) values '
                                                         '({}, "{}","{}")'.format(id_host, hunting_type, host_status))
            elif result['status'] != 'OK' and host_status == 'OK':
                HuntingModule.database_module.exec_query('UPDATE processed_host SET status="OK" WHERE id_host={}'
                                                         ' and hunting_type="{}"'.format(id_host, hunting_type))


        def add_processed_evos(self, id_session):

            query = 'SELECT hunting_type FROM channel WHERE name=(SELECT channel_name FROM session WHERE id={})'
            hunting_type = HuntingModule.database_module.exec_query(query.format(id_session))[0]['hunting_type']

            current_session_evos = HuntingModule.database_module.exec_query('SELECT * FROM session_evo WHERE id_session={}'
                                                                    .format(id_session))
            current_processed_evos = HuntingModule.database_module.exec_query('SELECT * FROM processed_evo WHERE hunting_type="{}"'
                                                                    .format(hunting_type))

            for s_evo in current_session_evos:

                #if s_evo['status'] == 'OK':
                found = False
                evo = None
                for p_evo in current_processed_evos:
                    if s_evo['hostname'] == p_evo['hostname'] and s_evo['evoname'] == p_evo['evo_name']:
                        found = True
                        evo = p_evo
                        break
                if not found:
                    query_insert = 'INSERT INTO processed_evo (hostname, evoname, hunting_type, status) values ("{}","{}","{}","{}")'
                    HuntingModule.database_module.exec_query(query_insert.format(s_evo['session_hostname'], s_evo['evo'],
                                                                                 hunting_type, s_evo['status']))
                else:
                    if evo['status'] != 'OK' and s_evo['status'] == 'OK':
                        HuntingModule.database_module.exec_query('UPDATE processed_evo SET status="OK" WHERE'
                                                                 ' hostname="{}" and evoname="{}" and hunting_type"{}"'.format(
                            s_evo['session_hostname'], s_evo['evo'], hunting_type
                        ))


        def store_historical_data(self, id_session):
            """
            Insert the information about hosts and evos from the current finished session into historical, and delete
            them from session_host and session_evo.
            :param id_session:
            :return: None
            """

            # Insert into historical the data of the session_host.
            query_host = 'INSERT INTO hist_session_host SELECT * FROM session_host WHERE id_session={}'.format(id_session)
            HuntingModule.database_module.exec_query(query_host)
            # Insert into historical the data of the session_evo.
            query_evo = 'INSERT INTO hist_session_evo SELECT id_session,session_hostname,id_job,evo, date_start, ' \
                        'date_finish, processing_host, status, exit_code FROM session_evo WHERE id_session={}'.format(
                id_session
            )
            HuntingModule.database_module.exec_query(query_evo)

            # Delete the data from the tables for current processing.
            query_delete_host = 'DELETE FROM session_host WHERE id_session={}'.format(id_session)
            HuntingModule.database_module.exec_query(query_delete_host)
            query_delete_evo = 'DELETE FROM session_evo WHERE id_session={}'.format(id_session)
            HuntingModule.database_module.exec_query(query_delete_evo)


        def task(self) -> None:
            logger.info('Init launching tasks')

            # Get working channels
            working_channels = self.get_working_channels()
            logger.info('Working channels: {}'.format(working_channels))

            # Ask forest (evidence processor) about these channels and update database with status
            for channel in working_channels:

                # Get the current working task for this channel.
                session = self.db.exec_query('SELECT * FROM session WHERE channel_name="{}" and status="{}"'.format(
                    channel['name'], __class__.STATUS_WORKING
                ))[0]

                # Execute the file parsing for the folder in path.
                task_finished = self.load_hunting_info_from_files(session)

                if not task_finished:
                    new_status = __class__.STATUS_WORKING
                else:
                    new_status = __class__.STATUS_FINISHED

                if new_status ==  __class__.STATUS_WORKING:
                    # TODO: llamar a método para que actualice el número actual de session_hosts procesados en funcion de los
                    # evos que han sido procesados.
                    pass
                # Update the status of the task if it has finished.
                elif new_status == __class__.STATUS_FINISHED:
                    self.db.exec_query('UPDATE session SET status="{}" WHERE id="{}"'.format(
                        new_status, session['id']
                    ))

                    # Get all the session_host processing
                    total_hosts_processed = self.db.exec_query(
                        'SELECT id_host FROM session_host WHERE id_session="{}" and status != "NOT_AVAILABLE"'.format(
                            session['id']
                        ))

                    for host_processing in total_hosts_processed:
                        hostname = self.db.exec_query('SELECT hostname FROM host WHERE id="{}"'.format(
                            host_processing['id_host']
                        ))[0]

                        total_evos_processed = self.db.exec_query(
                            'SELECT COUNT(*) AS total from session_evo WHERE id_session="{}" AND session_hostname LIKE "{}"'.format(
                                session['id'], hostname['hostname']
                            ))[0]

                        if total_evos_processed['total'] > 0:
                            host_date_start = self.db.exec_query(
                                'SELECT date_start FROM session_evo WHERE id_session="{}" AND session_hostname LIKE "{}" ORDER BY date_start ASC LIMIT 1'.format(
                                    session['id'], hostname['hostname']
                                ))[0]
                            host_date_finish = self.db.exec_query(
                                'SELECT date_finish FROM session_evo WHERE id_session="{}" AND session_hostname LIKE "{}" ORDER BY date_finish DESC LIMIT 1'.format(
                                    session['id'], hostname['hostname']
                                ))[0]
                            # Contamos que los evos KO son diferentes de OK y de SKIP
                            host_total_status_KO = self.db.exec_query(
                                'SELECT COUNT(status) FROM session_evo WHERE id_session="{}" AND session_hostname LIKE "{}" AND (status !="OK" OR status !="SKIP")'.format(
                                    session['id'], hostname['hostname']
                                ))[0]
                            host_status = "KO" if host_total_status_KO['COUNT(status)'] > 0 else 'OK'

                            #if host_status == 'OK':
                            # Add the host to processed_host if it has not been added yet.
                            self.add_processed_host(host_processing['id_host'], channel['hunting_type'], host_status)
                            if host_status == 'KO':
                                new_status = __class__.STATUS_FAILED

                        else:
                            new_status = __class__.STATUS_FAILED
                            host_date_start = self.db.exec_query(
                                'SELECT date_start FROM session WHERE id="{}" '.format(
                                    session['id']
                                ))[0]
                            host_date_finish = self.db.exec_query(
                                'SELECT date_finish FROM session WHERE id="{}" '.format(
                                    session['id']
                                ))[0]

                            host_status = 'NO_EVOS'

                        self.db.exec_query(
                            'UPDATE session_host SET date_start="{}", date_finish="{}", status="{}" WHERE id_session="{}" AND id_host="{}"'.format(
                                host_date_start['date_start'], host_date_finish['date_finish'], host_status, session['id'],
                                host_processing['id_host']
                            ))

                        # Update the session status
                        if new_status == __class__.STATUS_FAILED:
                            self.db.exec_query('UPDATE session SET status="{}" WHERE id="{}"'.format(
                                new_status, session['id']
                            ))
                    self.store_historical_data(session['id'])


            # Get all channels
            channels = HuntingModule.get_all_channels()
            # Filter only active channels
            active_channels = [c for c in channels if self.is_channel_active(c) and c['name'] != 'manual']
            logger.info('Active channels: {}'.format(active_channels))

            # Iterate active channels and launch work for forest
            for channel in active_channels:
                self.launch_task(channel)

            logger.info('Tasks launched')

        def load_hunting_info_from_files(self, task_info) -> bool:
            new_full_path = ''
            finished = False
            connection = sqlite3.connect(HuntingModule.database_for_panda)

            ps_header = HuntingModule.csv_headers.get('ps')
            evos_header = HuntingModule.csv_headers.get('evos')
            hits_header = HuntingModule.csv_headers.get('hits')
            full_path = task_info.get('forest_path')
            session_id = task_info.get('id')
            current_evos = task_info.get('current_evos')
            current_hits = task_info.get('current_hits')

            files = sorted(os.listdir(full_path))

            try:
                for file in files:
                    full_file_path = os.path.join(full_path, file)
                    if file.startswith('ps-hunting-'):
                        with open(full_file_path) as f:
                            first_line = f.readline()
                            ps_info = first_line.split()
                            total_evos = ps_info[0]
                            start_date = ps_info[1]
                            finish_date = 0

                            if len(ps_info) == 3:
                                finish_date = ps_info[2]
                                finished = True

                            query = 'UPDATE session SET total_evos={}, date_start={}, date_finish={} WHERE id={}'.format(
                                total_evos, start_date, finish_date, session_id)
                            self.db.exec_query(query)
                    elif file.startswith('evos-hunting-'):
                        (new_full_path, new_evos) = self.preprocess_evos_file(full_path, file, skip_rows=current_evos)
                        self.ps.load_csv_to_database(new_full_path, connection, 'session_evo', header=evos_header)
                        os.remove(new_full_path)

                        query = 'UPDATE session_evo SET id_session={} WHERE id_session=-1'.format(session_id)
                        self.db.exec_query(query)

                        total_evos = current_evos + new_evos
                        query = 'UPDATE session SET current_evos={} WHERE id={}'.format(total_evos, session_id)
                        self.db.exec_query(query)

                        self.add_processed_evos(session_id)


                    elif file.startswith('hits-hunting-'):
                        (new_full_path, new_hits) = self.preprocess_hits_file(full_path, file, skip_rows=current_hits)
                        self.ps.load_csv_to_database(new_full_path, connection, 'session_hit', header=hits_header)
                        os.remove(new_full_path)

                        total_hits = current_hits + new_hits
                        query = 'UPDATE session SET current_hits={} WHERE id={}'.format(total_hits, session_id)
                        self.db.exec_query(query)

                    elif file.startswith('hosts_list'):
                        # Check if file is read
                        query_evos_read = 'SELECT COUNT(*) AS total FROM session_host WHERE id_session={} AND total_evos={}'.format(
                                session_id, -1)
                        is_read = True if query_evos_read[0]['total'] == 0 else False

                        if not is_read:
                            with open(full_file_path) as f:
                                first_line = f.readline()
                                hosts_list_info = first_line.split()
                                hostname = hosts_list_info[0]
                                ip = hosts_list_info[1]

                                if len(hosts_list_info) == 3:
                                    total_evos = hosts_list_info[2]

                                    query_host = 'SELECT id FROM host WHERE hostname="{}" AND ip="{}"'.format(
                                        hostname, ip)
                                    id_host = query_host[0]['id']

                                    query = 'UPDATE session_host SET total_evos={} WHERE id_session={} AND id_host={}'.format(
                                        total_evos, session_id, id_host)
                                    self.db.exec_query(query)

            except Exception as e:
                if os.path.isfile(new_full_path):
                    os.remove(new_full_path)

            # return (loaded, errors_full_path)
            return finished

        def preprocess_evos_file(self, full_path, file, sep=' ', skip_rows=0):
            file_path = os.path.join(full_path, file)
            new_file_path = os.path.join(full_path, 'aux_evos.txt')
            file_errors_path = os.path.join(full_path, 'aux_evos_error.txt')

            with open(file_path, 'r') as f:
                lines = f.readlines()

            content = [line.replace('-live-', sep) for line in lines[skip_rows:]]
            content_cleaned = list()
            content_errors = list()
            line_number = skip_rows
            for line in content:
                line_number = line_number + 1
                if len(line.split(sep)) == 8:
                    content_cleaned.append(line)
                else:
                    content_errors.append('Line {}: {}'.format(line_number, line))

            with open(new_file_path, 'w') as f:
                f.writelines(content_cleaned)

            with open(file_errors_path, 'a+') as f:
                f.writelines(content_errors)

            return (new_file_path, len(content_cleaned))

        def preprocess_hits_file(self, full_path, file, sep=' ', skip_rows=0):
            file_path = os.path.join(full_path, file)
            new_file_path = os.path.join(full_path, 'aux_hits.txt')
            file_errors_path = os.path.join(full_path, 'aux_hits_error.txt')

            with open(file_path, 'r') as f:
                lines = f.readlines()

            content = [line.replace('-live-', sep, 1) for line in lines[skip_rows:]]
            content_cleaned = list()
            content_errors = list()
            line_number = skip_rows
            for line in content:
                line_number = line_number + 1
                if len(line.split(sep)) == 5:
                    content_cleaned.append(line)
                else:
                    content_errors.append('Line {}: {}'.format(line_number, line))

            with open(new_file_path, 'w') as f:
                f.writelines(content_cleaned)

            with open(file_errors_path, 'a+') as f:
                f.writelines(content_errors)

            return (new_file_path, len(content_cleaned))

    class AgentStatusTask(TaskThread):

        def __init__(self, db: DatabaseModule, scm: SystemCommandsModule) -> None:
            TaskThread.__init__(self)
            self.db = db
            self.scm = scm

        def task(self) -> bool:

            logger.info('Executing AgentStatusTask')
            second_most_recent_file = None
            bad_lines = list()

            # Read all the files in directory and filter only the reports of agent status.
            agent_status_files = [f for f in os.listdir(HuntingModule.agent_status_folder) if
                                  f.startswith('hunting_report_status_from_scope')]

            # If there are less than 2 report files, end the execution.
            if len(agent_status_files) < 2:
                logger.info('There are only {} hunting_report_status_from_scope files. Exiting...'.format(
                    len(agent_status_files)))
                return False

            # Extract the timestamps of the report files.
            timestamps = list()
            for f in agent_status_files:
                timestamps.append(int(f.split('_')[-1].split('.')[0]))

            # Order the timestamps, and find the second most recent report file.
            timestamps.sort(reverse=True)
            for f in agent_status_files:
                if f.endswith('{}.txt'.format(str(timestamps[1]))):
                    second_most_recent_file = f
                    break

            logger.info('Updating agents status from file: {}'.format(second_most_recent_file))
            # Open the file, parse its content and update the corresponding host
            if second_most_recent_file is not None:
                with open(os.path.join(HuntingModule.agent_status_folder, second_most_recent_file), 'r') as agent_file:

                    for line in agent_file.readlines():
                        # Check if the line has a correct format.
                        if __class__.is_line_ok(line):
                            parsed_line = line.split(',')
                            ip = parsed_line[0]
                            hostname = parsed_line[1]
                            status = 0 if (parsed_line[2] == 'down') else 1

                            self.db.exec_query(
                                'UPDATE host SET agent_available={} WHERE hostname like "{}" and ip="{}" COLLATE NOCASE'.format(
                                    status, hostname, ip
                                ))
                        else:
                            bad_lines.append(line)
            logger.info('Updating agents status finished. {} lines could not be read from report file.'.format(
                len(bad_lines)))
            logger.debug('Bad lines: {}'.format(bad_lines))

        @staticmethod
        def is_line_ok(line):
            """
            Check if a line from report status file has the correct format
            :param line: line of the file to check
            :return: True if line is correct, False otherwise.
            """
            split = line.split(',')
            # Line has almost 3 fields
            if len(split) < 4:
                return False
            # First field (ip) must have at least 7 characters. Third field (status) must have at least 2 characters.
            if len(split[0]) < 7 or len(split[2]) < 2:
                return False

            return True
