import logging
import json

from flask import jsonify, request

from common.module import ViewModule, authenticate
from common.infra_tools.decorators import log_function
from common.infra_modules.infra_exception import AppException

from factory_modules.hunting_module import MODULE_NAME
#from factory_modules.hunting_module.hunting_module import HuntingModule


logger = logging.getLogger(MODULE_NAME)


# @authenticate()
class HuntingModuleChannelView(ViewModule):
    excluded_methods = ["return200"]

    def get(self, name):

        result = self.app_module.get_channel(name)
        return json.dumps(result)

    def all(self):
        result = self.app_module.get_channels()
        return json.dumps(result)

    def post(self):
        input = request.json

        try:
            self.app_module.add_channel(input)
            result = self.return200(True)
        except Exception as err:
            result = self.return200(False)

        return result

    def put(self):
        input = request.json

        try:
            self.app_module.update_channel(input)
            result = self.return200(True)
        except Exception as err:
            print(err)
            result = self.return200(False)

        return result


    def remove(self, name):

        try:
            self.app_module.delete_channel(name)
            result = self.return200(True)
        except Exception as err:
            print(err)
            result = self.return200(False)

        return result


    @log_function(logger)
    def return200(self, success: bool):
        resp = jsonify(success=success)
        resp.status_code = 200

        return resp


class HuntingModuleHostView(ViewModule):
    excluded_methods = ["return200"]

    # get all hosts info
    @log_function(logger)
    def hosts(self):
        hosts = self.app_module.get_host_data()

        return json.dumps(hosts, ensure_ascii=True)


    # read csv with hosts from file path and store in database
    @log_function(logger)
    def post(self):
        loaded = False

        try:
            xlsx_params = request.json
            loaded = self.app_module.load_hosts_xlsx(xlsx_params)
        except Exception as e:
            pass

        # success = self.return200(loaded, errors_file_path=errors_full_path)
        success = self.return200(loaded)

        return success


    # change host channels from channel1 to channel2
    @log_function(logger)
    def put(self):
        success = self.return200(True)

        try:
            request_parameters = request.json
            old_channel = request_parameters.get('old_channel')
            new_channel = request_parameters.get('new_channel')
            self.app_module.update_hosts_channel(old_channel, new_channel)
        except Exception as e:
            success = self.return200(False)

        return success


    @log_function(logger)
    def return200(self, success: bool, errors_file_path=None):
        resp = jsonify(success=success, errors_file_path=errors_file_path)
        resp.status_code = 200

        return resp


class HuntingModuleHistoricalCsvView(ViewModule):
    excluded_methods = ["return200"]

    @log_function(logger)
    def get(self):
        historical_csv = self.app_module.get_historical_csv()
        return json.dumps(historical_csv, ensure_ascii=True)



    @log_function(logger)
    def return200(self, success: bool):
        resp = jsonify(success=success)
        resp.status_code = 200

        return resp


class HuntingModuleEvidenceOutputsView(ViewModule):
    excluded_methods = ["return200"]


    @log_function(logger)
    def post(self):
        loaded = False

        try:
            task_info = request.json
            (loaded, finished) = self.app_module.load_hunting_info_from_files(task_info)
        except Exception as e:
            pass

        success = self.return200(loaded)

        return success


    @log_function(logger)
    def return200(self, success: bool):
        resp = jsonify(success=success)
        resp.status_code = 200

        return resp


class HuntingModuleReportView(ViewModule):
    excluded_methods = ["return200"]

    def total(self):
        result = self.app_module.get_report_total()
        return json.dumps(result)

    def channels(self):
        result = self.app_module.get_report_total_by_channel()
        return json.dumps(result)

    def details(self, channel_name):
        result = self.app_module.get_report_details_by_channel(channel_name)
        return json.dumps(result)

    def evos(self, channel_name):
        result = self.app_module.get_report_evos_details_by_channel(channel_name)
        return json.dumps(result)

    def yesterday(self):
        result = self.app_module.get_yesterday_report_by_channel()
        return json.dumps(result)

    def history(self):
        result = self.app_module.get_history_report()
        return json.dumps(result)

    def agents(self, status):
        result = self.app_module.get_report_agents_status(status)
        return json.dumps(result)

    def hits(self):
        result = self.app_module.get_report_hits()
        return json.dumps(result)

    def progress(self):
        result = self.app_module.get_report_session_working()
        return json.dumps(result)


class HuntingModuleManualView(ViewModule):
    excluded_methods = ["return200"]

    def post(self):
        data = request.json
        result = self.app_module.execute_manual_hunting(data)
        return json.dumps(result)

    def channel(self, channel_name, times):
        result = self.app_module.execute_manual_channel(channel_name, times)
        return json.dumps(result)

    def stop(self, channel_name):
        result = self.app_module.stop_manual_channel(channel_name)
        return json.dumps(result)
