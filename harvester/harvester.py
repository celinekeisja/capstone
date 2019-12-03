import configparser
import getpass as gp
import logging.config
import os
import re
from urllib.parse import urljoin

import psycopg2
import wget
import yaml
from bs4 import BeautifulSoup
from requests import get, post

import db_manager as db


# 1st password: docker
# 2nd password: docker


def upload(file_name):
    url = 'http://localhost:8000/web_service_db/upload'
    
    file = {file_name: open(file_name, 'rb')}
    r = post(url, files=file)
    status_code = r.status_code
    return status_code


def re_download(url, href, file_type):
    # delete existing file
    delete_file(href, file_type)

    # download updated file
    download_file(url, href, file_type)


def compare_versions(soup, href, conn, file_name, file_type):
    # getcurrent version
    curr_version = float(get_version(soup, href, file_type))

    # get version in table
    db_version = float(db.get_recorded_version(conn, file_name))
    if curr_version > db_version:
        return True
    else:
        return False


def check_updates(soup, conn, href, url, file_name, file_type):
    """Check if the file has been updated and then re-download all files."""

    logger.info(f'Determining if version of {file_name} is new..')
    if compare_versions(soup, href, conn, file_name, file_type):
        logger.info(f'Attempting to re-download {file_name}..')
        try:
            re_download(url, href, file_type)
        except:
            logger.error('Unable to redownload file')
        logger.info(f'Updating record of {file_name} in table..')
        # update existing tracking data to table
        db.update_record(conn, get_version(soup, href, file_type), file_name)

        # upload(file_name)


def extract_data(file_name, version):
    """Saves the extracted data into a dictionary to be inserted in the table."""
    file_version_data = {"file_name": file_name,
                         "version": version}
    return file_version_data


def extract_complete_filename(href, file_type):
    """Extract the complete file name of the file."""
    logger.info(f'Extracting complete file name from {href}..')
    if file_type == 'main':
        try:
            file_name = href.split('/')[2]
        except:
            file_name = href
    elif file_type == 'trans':
        file_name = href.split('/')[1]
    return file_name


def get_version(soup, href, file_type):
    """Get the version of the main file."""
    logger.info(f'Getting the version of {href}..')
    if file_type == 'main':
        table = soup.find("table", attrs={"class": "utilcaption"})
        all_tr = table.find_all("tr")
        td = all_tr[0].find_all("td")
        version = re.search('\d\.\d\d', td[1].text)
        version = version.group(0)
    elif file_type == 'trans':
        all_a = soup.find('a', attrs={'href': href}).parent.parent
        all_td = all_a.find_all('td')
        try:
            version = re.search('\d\.\d\d', all_td[-1].text)
            version = version.group(0)
        except:
            version = ''
    return version


def download_file(url, href, file_type):
    """Download file to specified path."""
    config = setup_config()
    logger.info(f'Preparing to download {href}..')
    file = urljoin(url, href)
    if file_type == 'main':
        try:
            path = '{}{}'.format(config['harvester']['download_path'], href.split('/')[2])
        except:
            path = '{}{}'.format(config['harvester']['download_path'], href)
    elif file_type == 'trans':
        path = '{}{}'.format(config['harvester']['download_path'], href.split('/')[1])
    logger.info(f'Downloading {file}..')

    request = get(file)
    with open(path, 'wb') as file:
        file.write(request.content)
    logger.info(f'Downnloaded {file}.')
    return "Successfully downloaded file."


def delete_file(href, file_type):
    """Delete file from local disk."""

    config = setup_config()
    if file_type == 'main':
        try:
            path = '{}{}'.format(config['harvester']['download_path'], href.split('/')[2])
        except:
            path = '{}{}'.format(config['harvester']['download_path'],href)
    elif file_type == 'trans':
        path = '{}{}'.format(config['harvester']['download_path'], href.split('/')[1])
    os.remove(path)
    logger.info(f"Successfully deleted {href}.")


def crawl(base_url, url, unqs, conn):
    response = get(url)
    soup = BeautifulSoup(response.text, 'lxml')
    html_links = soup.find_all('a', href=True)
    for link in html_links:
        href = link['href']
        if href not in unqs:  # think need to remove this
            if link.has_attr('class'):
                if link['class'][0] == 'downloadline' and (href.endswith('exe') or href.endswith('zip')):
                    logger.info("Main file: {}".format(href))
                    file_type = 'main'
                    # extracting complete file name
                    file_name = extract_complete_filename(href, file_type)

                    # checks if the file has an existing record in the table
                    if db.exists(conn, file_name):
                        # checks if the file has been updated
                        check_updates(soup, conn, href, url, file_name, file_type)

                    else:
                        # downloading file
                        download_file(url, href, file_type)

                        # get file version
                        version = get_version(soup, href, file_type)

                        # extracting tracking data
                        file_version_data = extract_data(file_name, version)

                        # inserting tracking data to table
                        db.database_insert(conn, file_version_data)

            elif href.startswith('utils'):
                logger.info("Downloads page: {}{}".format(base_url, href))
                loc = "{}{}".format(base_url, href)
                crawl(base_url, loc, unqs, conn)

            elif (href.endswith('zip') or href.endswith('exe')) and href.startswith('trans'):
                logging.info("Translation file: {}".format(href))
                file_type = 'trans'

                # getting complete file name
                file_name = extract_complete_filename(href, file_type)

                if db.exists(conn, file_name):
                    check_updates(soup, conn, href, url, file_name, file_type)
                else:
                    # downloading file
                    download_file(url, href, file_type)

                    # extracting file version
                    version = get_version(soup, href, file_type)

                    # extracting tracking data
                    file_version_data = extract_data(file_name, version)

                    # inserting tracking data to table
                    db.database_insert(conn, file_version_data)
            unqs.append(href)


def setup_logging(default_path='logging.yaml',
                  default_level=logging.INFO,
                  env_key='Log_CFG'):
    path = default_path
    value = os.getenv(env_key, None)
    if value:
        path = value
    if os.path.exists(path):
        with open(path, 'rt') as f:
            config = yaml.safe_load(f.read())
        logging.config.dictConfig(config)
    else:
        logging.basicConfig(level=default_level)
    return 'Setting up logging.'


def setup_config():
    config = configparser.ConfigParser()
    config.read('./config.ini')
    return config


def main():
    config = setup_config()
    links = []
    setup_logging()

    # Database configs
    hostname = config['harvester']['hostname']
    username = config['harvester']['username']
    password = config['harvester']['password']
    db.check_database(hostname, username, password)
    connection = db.database_connection(hostname,
                                        username,
                                        password,
                                        config['harvester']['port'],
                                        config['harvester']['database'])
    db.create_table(connection)

    base_url = config['main']['url']
    crawl(base_url, base_url, links, connection)
    db.close_connection(connection)


if __name__ == "__main__":
    # while True:
    logger = logging.getLogger(__name__)
    main()
    # time.sleep(60)
