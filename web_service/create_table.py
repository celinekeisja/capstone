import psycopg2


def create():
    """Create a table to store an ID, Parent Path, File Name, File Size, MD5 Hash and SHA1 Hash."""
    connection = psycopg2.connect(user='postgres',
                                  password='password',
                                  host='127.0.0.1',
                                  port=59945,
                                  database='web_service_db')
    table_cursor = connection.cursor()
    create_table_query = """CREATE TABLE IF NOT EXISTS file_data(
                            ID SERIAL PRIMARY KEY NOT NULL,
                            FILE_NAME TEXT NOT NULL,
                            FILE_TYPE TEXT,
                            FILE_SIZE INT NOT NULL,
                            MD5 TEXT NOT NULL,
                            SHA1 TEXT NOT NULL);"""
    table_cursor.execute(create_table_query)
    connection.commit()


create()
