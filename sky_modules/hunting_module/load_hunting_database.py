import sqlite3 as sqlite

class HuntingDatabase(object):

    @staticmethod
    def create_hunting_database(database, sql_script):

        try:
            connection = sqlite.connect(database)
            cursor = connection.cursor()

            script_file = open(sql_script, 'r')
            script = script_file.read()
            script_file.close()

            cursor.executescript(script)

            connection.commit()
        except Exception as e:
            pass
        finally:
            connection.close()

