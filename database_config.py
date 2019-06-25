import psycopg2
import json
import os


class Database:

    # connect local postgres
    def __init__(self, file_name, environment, datasource):
        self.file_name = file_name
        self.environment = environment
        self.datasource = datasource
        self.config_data = self.__read_db_config_file(file_name)

    def __read_db_config_file(self, file_name):
        __name__ = 'resources'
        __location__ = os.path.join(os.path.dirname(__file__), 'resources/' + file_name)
        try:
            file = open(os.path.join(os.path.dirname(__file__), 'resources/' + file_name))
            return json.load(file)

        except FileNotFoundError as error:
            print('can\' find file:' + file_name, error)

    def __get_connection(self):
        try:
            connection = psycopg2.connect(user=self.config_data[self.environment][self.datasource]['user'],
                                          password=self.config_data[self.environment][self.datasource]['password'],
                                          host=self.config_data[self.environment][self.datasource]['host'],
                                          port=self.config_data[self.environment][self.datasource]['port'],
                                          database=self.config_data[self.environment][self.datasource]['database'])
            return connection
        except (Exception, psycopg2.Error) as error:
            print('Error while connecting to database', error)

    def __close_connection(self, conn):
        if conn:
            conn.close()

    pass

    # create %s,%s,%s,%s,%s...
    def __create_parameter_template(self, first_row):
        value = ''
        for i in range(len(list(first_row))):
            value += '%s,'
        return value[:-1]

    def persist_data_to_table(self, table_name, job_data):
        if type(job_data) is not list:
            raise TypeError('Invalid data type require list')
        if type(job_data[0]) is not dict:
            raise TypeError('Invalid data type require dictionary')

        columns = ', '
        first_row = job_data[0]
        first_row['publish_date'] = 0  # need to format from string to bigInt
        column_list = list(first_row.keys())
        columns = columns.join(column_list)
        cur = None
        conn = None
        try:
            conn = self.__get_connection()
            list_of_row_data_in_tup = [tuple(row.values()) for row in job_data]
            tup = list_of_row_data_in_tup[0]
            cur = conn.cursor()
            records_list_template = ','.join(['%s'] * len(first_row.values()))
            records_list_template = '(' + records_list_template + ')'
            insert_query = 'insert into ' + table_name + ' (' + columns + ') VALUES {}'.format(
                records_list_template)
            # print(cur.mogrify(insert_query, tup).decode('utf8'))
            cur.execute(insert_query, tup)
            conn.commit()
            return cur.rowcount
        except psycopg2.Error as e:
            raise e
        finally:
            cur.close()
            self.__close_connection(conn)

    def check_ad_is_exist(self, job_id):
        temp_job_id = int(job_id)
        check_exist_query = "SELECT job_id from job WHERE job_id = %s"
        cur = None
        conn = None
        try:
            conn = self.__get_connection()
            cur = conn.cursor()
            cur.execute(check_exist_query, (temp_job_id,))
            return cur.fetchall()
        except psycopg2.Error as e:
            raise e
        finally:
            cur.close()
            self.__close_connection(conn)

    def get_all_job_content(self):
        conn = None
        cur = None
        try:
            conn = self.__get_connection()
            cur = conn.cursor()
            query = 'SELECT job_id, content FROM public.job'
            cur.execute(query)
            return cur.fetchall()
        except psycopg2.Error as e:
            raise e
        finally:
            cur.close()
            self.__close_connection(conn)

    def update_job_content(self, data):
        conn = None
        cur = None
        try:
            conn = self.__get_connection()
            cur = conn.cursor()

            # UPDATE "public"."job" SET "salary" = '1' WHERE "job_id" = 39305265
            query = 'UPDATE public.job SET content =  %(content)s WHERE job_id= %(job_id)s'
            cur.executemany(query, data)
            conn.commit()
            print(str(cur.rowcount))
        except psycopg2.Error as e:
            raise e
        finally:
            cur.close()
            self.__close_connection(conn)
