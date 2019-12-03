from harvester import psycopg2, gp, __name__ as name
import logging.config

logger = logging.getLogger(name)


def check_database(hostname, username, password):
    """Check if desired database exists. Otherwise, call a function to create desired database."""
    try:
        def_connection = psycopg2.connect(user=username,
                                          password=password,
                                          host=hostname,
                                          port="54320",
                                          database="postgres")
        def_connection.autocommit = True

        db_cursor = def_connection.cursor()
        check_db_query = """SELECT COUNT(*) FROM pg_catalog.pg_database
                            WHERE datname = 'harvest_db';"""
        db_cursor.execute(check_db_query)
        if db_cursor.fetchone()[0] == 0:
            create_database(db_cursor)

        db_cursor.close()
        def_connection.close()
    except Exception as e:  
        logger.error(f"Error in creating database - {e}")


def create_database(cursor):
    """Create the desired database."""
    try:
        query = """CREATE DATABASE harvest_db;"""
        cursor.execute(query)
    except Exception as e:
        logger.error(f"Error in creating database - {e}")


def create_table(table_connection):
    """Create a table to store an ID, Parent Path, File Name, File Size, MD5 Hash and SHA1 Hash."""
    try:
        table_cursor = table_connection.cursor()
        create_table_query = """CREATE TABLE IF NOT EXISTS file_versions(
                                ID SERIAL PRIMARY KEY NOT NULL,
                                FILE_NAME TEXT NOT NULL,
                                VERSION TEXT NOT NULL);"""
        table_cursor.execute(create_table_query)
        table_connection.commit()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(f"Error while creating table - {error}.")


def update_record(conn, version, file_name):
    """Update record in table."""
    cursor = conn.cursor()
    logger.info(f'Updating record for {file_name} in table..')
    try:
        try:
            update_query = '''UPDATE file_versions SET version = %s WHERE file_name = %s'''
            logger.info(f'Executing record version to {version}.')
            cursor.execute(update_query, (version, file_name,))
            conn.commit()
        except (Exception, psycopg2.Error) as error:
            logger.error(f"Unable to update record - {error}")
    except (Exception, psycopg2.Error) as error:
        logger.error(error)
    finally:
        cursor.close()
    return 'Updated record.'


def get_recorded_version(conn, file_name):
    """Gets the version of file in the table."""
    cursor = conn.cursor()
    select_query = '''SELECT version FROM file_versions WHERE file_name =  %s'''

    logger.info(f'Selecting current version of {file_name} in table..')
    cursor.execute(select_query, (file_name,))
    fetched = cursor.fetchone()
    cursor.close()
    return fetched[0]


def exists(conn, file_name):
    """Check if the file has an existing record in the table."""
    cursor = conn.cursor()
    query = '''SELECT EXISTS ( SELECT 1 
                                FROM file_versions
                                WHERE file_name = %s)'''

    logger.info(f'Checking if {file_name} has an existing record in the table..')
    cursor.execute(query, (file_name,))
    return cursor.fetchone()[0]


def close_connection(connection):
    """Close the database connection."""
    logger.info('Closing connection')
    connection.close()


def database_connection(hostname, username, password, port, database):
    """Connect to the database."""
    logger.info('Connecting to the database..')
    try:
        connection = psycopg2.connect(user=username,
                                      password=password,
                                      host=hostname,
                                      port=port,
                                      database=database)
        return connection
    except Exception as e:
        logger.error(f"Error in connection - {e}")


def database_insert(connection, file):
    """Insert records of files in a database."""
    cursor = connection.cursor()
    try:
        try:
            insert_query = """INSERT INTO file_versions 
            (FILE_NAME, VERSION) 
            VALUES (%s, %s);"""
            record_to_insert = (file['file_name'],
                                file['version'])
            logger.info(f'Inserting {file["file_name"]} record in the table..')
            cursor.execute(insert_query, record_to_insert)
            connection.commit()
        except (Exception, psycopg2.Error) as error:
            logger.error(f"Unable to insert record - {error}")
    except (Exception, psycopg2.Error) as error:
        logger.error(error)
    finally:
        if connection:
            cursor.close()
