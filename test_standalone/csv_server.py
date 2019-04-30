import collections
import fabric
import json
import logging
import logging.handlers
import pandas as pd
import re
import sqlite3
from flask import Flask, request, jsonify


# DEPENDENCIES: pip3 install pandas fabric flask


# Main params
HOST = '0.0.0.0'
PORT = 6000
CSV_FILE = 'test.csv'
DATABASE = "test.db"
TABLE_NAME = "csv"

# Index of data
PRIMARY_KEY_FIELD = 'policyID'

# Status column
STATUS_COLUMN = 'status'

# Logger configuratino
LOG_LEVEL = logging.DEBUG
LOG_FORMATTER = logging.Formatter('%(asctime)s %(levelname)-8s - %(message)s')
logger = logging.getLogger('csv_server')
logger.setLevel(LOG_LEVEL)
ch = logging.StreamHandler()
ch.setLevel(LOG_LEVEL)
ch.setFormatter(LOG_FORMATTER)
rfh = logging.handlers.RotatingFileHandler('csv_server.log', 'a', 104857600, 10)
rfh.setLevel(LOG_LEVEL)
rfh.setFormatter(LOG_FORMATTER)
# logger.addHandler(ch)
logger.addHandler(rfh)


# Init flask app
app = Flask(__name__)

# CSV data
data = collections.OrderedDict()


def start_api():
    logger_flask = logging.getLogger('werkzeug')
    for hdlr in logger_flask.handlers[:]:  # remove all old handlers
        logger_flask.removeHandler(hdlr)

    debug = False
    ssl = None
    logger.info('REST API starting')
    app.run(host=HOST, port=PORT, debug=debug, use_reloader=False, threaded=True, ssl_context=ssl)


def db_exec(query: str):
    # Execute query and return cursor
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute(query)
        return conn, cur
    except sqlite3.Error as e:
        print(e)

    return None, None


def execute_command(command: str, sudo=False, host='localhost', user=None, password=None, port=None):
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
    if is_localhost:
        conn = fabric.Connection(host)
        modified_command = 'sudo ' + command if sudo else command
        logger.info('Executing command " {} " in {} as sudo={}'.format(modified_command, host, sudo))
        output = conn.local(modified_command)
    else:
        conn = fabric.Connection(host, user=user, port=port)
        if password and len(password) > 0:
            conn.connect_kwargs.look_for_keys = False
            conn.connect_kwargs.password = password

        logger.info('Executing command " {} " in {} as sudo={}'.format(command, host, sudo))
        output = conn.sudo(command) if sudo else conn.run(command)

    return output.stdout, output.stderr


def return200(success: bool):
    resp = jsonify(success=success)
    resp.status_code = 200
    return resp


def load_csv_in_memory():
    # Select all files from database and loads into dictionary
    # If you want sorted data simply write ORDER BY in select
    conn, cur = db_exec('SELECT * FROM {}'.format(TABLE_NAME))

    if conn is None:
        logger.info('Loading csv into database')
        load_csv_into_database()
        logger.info('CSV loaded into database')
        conn, cur = db_exec('SELECT * FROM {}'.format(TABLE_NAME))

    result = [dict(row) for row in cur.fetchall()]

    for row_as_dict in result:
        data[row_as_dict[PRIMARY_KEY_FIELD]] = row_as_dict

    logger.info('CSV load into memory: {} entries'.format(len(result)))


def load_csv_into_database():
    conn = sqlite3.connect(DATABASE)
    for chunk in pd.read_csv(CSV_FILE, chunksize=1000):
        chunk.to_sql(name=TABLE_NAME, con=conn, if_exists='append', index=False)
    conn, cur = db_exec('ALTER TABLE {} ADD {} TEXT DEFAULT "" NULL'.format(TABLE_NAME, STATUS_COLUMN))
    conn.commit()


@app.route('/loadcsv')
def load_csv():
    load_csv_in_memory()
    return return200(True)


@app.route('/resetstatus')
def reset_status():
    # Reset column status to value
    columntoupdate = request.args.get('columntoupdate')
    value = request.args.get('value')
    conn, cur = db_exec('UPDATE {} SET {}="{}"'.format(TABLE_NAME, columntoupdate, value))
    conn.commit()
    return return200(True)


@app.route('/deleteduplicated')
def delete_duplicated():
    # Delete duplicated entries in table
    groupcols = request.args.get('columns')
    conn, cur = db_exec('DELETE FROM {} WHERE rowid NOT IN (SELECT min(rowid) FROM {} GROUP BY {})'.format(TABLE_NAME, TABLE_NAME, groupcols))
    conn.commit()

    return return200(True)


@app.route('/read')
def read_csv():
    # Return data memory as json
    output_as_json = json.dumps(data)
    logger.info('/read --> return data')
    return output_as_json


@app.route('/setstatus')
def set_status():
    """
    Args: id, column, value
    :return: update column with value in row id
    """
    id = request.args.get('id')
    column_to_update = request.args.get('column')
    value = request.args.get('value')
    query = 'UPDATE {} SET {}="{}" WHERE {}={}'.format(TABLE_NAME, column_to_update, value, PRIMARY_KEY_FIELD, id)
    conn, cur = db_exec(query)
    conn.commit()

    logger.info('/setstatus --> update column {} with value {} at row with id {}'.format(column_to_update, value, id))

    return return200(True)


@app.route('/execute', methods=['POST'])
def execute():
    input = request.json
    command = input['command']
    arguments = input['args']
    sudo = True if input['sudo'] == 'True' else False

    logger.info('/execute --> Trying to execute {} {} with sudo={}'.format(command, arguments, sudo))

    try:
        out, err = execute_command('{} {}'.format(command, arguments), sudo=sudo)
        logger.info('/execute --> Command executed with output \n{}'.format(out))
        success = True
    except Exception:
        logger.error('/execute --> Executed command error', exc_info=True)
        success = False

    return return200(success)


load_csv_in_memory()
start_api()