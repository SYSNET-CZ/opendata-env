import datetime
import logging
import os
import sys
import yaml

from defaults import CRON_MAP, ES_CONFIG, JASU_CONFIG_DEFAULT, FILENAMES_DICTIONARY_DEAFULT, DATA_SOURCE_DICTIONARY

DEBUG = os.getenv("DEBUG", 'True').lower() in ('true', '1', 't')
TEST = os.getenv("TEST_INSTANCE", 'True').lower() in ('true', '1', 't')
LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(levelname)s in %(module)s: %(message)s')
LOG_DATE_FORMAT = os.getenv('LOG_DATE_FORMAT', '%d.%m.%Y %H:%M:%S')
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # This is your Project Root
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, os.pardir))
EXPORT_DATA_DIR = os.getenv('EXPORT_DATA_DIR', os.path.join(ROOT_DIR, 'data'))
CONFIG_DIR = os.getenv('CONFIG_DIR', os.path.join(ROOT_DIR, 'conf'))
CSV_OUTPUT_DIRECTORY = EXPORT_DATA_DIR
CONFIG_FILE_NAME = 'opendata.yml'
CONFIG_TEST_FILE_NAME = 'opendata-test.yml'
CONFIG_FILE_PATH = os.path.join(CONFIG_DIR, CONFIG_TEST_FILE_NAME)
if not TEST:
    CONFIG_FILE_PATH = os.path.join(CONFIG_DIR, CONFIG_FILE_NAME)

CSV_FILE_SUFFIX = '_{}.csv'.format(datetime.datetime.now().strftime('%Y-%m-%d'))
CSV_FILE_NAME_TEST = 'test{}'.format(CSV_FILE_SUFFIX)


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Log(object, metaclass=Singleton):
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        handler = logging.StreamHandler(sys.stdout)
        if DEBUG:
            self.logger.setLevel(logging.DEBUG)
            handler.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)
            handler.setLevel(logging.INFO)
        formatter = logging.Formatter(fmt=LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
        handler.setFormatter(formatter)
        if self.logger.hasHandlers():
            self.logger.handlers.clear()
        self.logger.addHandler(handler)
        self.logger.propagate = False
        self.logger.info('LOG created')


def set_ext_logger(ext_logger):
    if ext_logger is not None:
        LOG.logger = ext_logger


def isfloat(value):
    try:
        float(value)
        return True
    except ValueError:
        return False


def get_this_year():
    out = datetime.datetime.now().year
    return out


def get_last_year():
    out = datetime.datetime.now().year
    out -= 1
    return out


def get_before_last_year():
    out = datetime.datetime.now().year
    out -= 2
    return out


def create_map_from_list(source_list):
    out = {}
    for item in source_list:
        for k in item.keys():
            out[k] = item[k]
    return out


def consolidate_date(value: str):
    if value is None:
        return None
    date_string_iso = None
    value_array = value.split(' ')
    date_string = value_array[0]
    d = date_string.split('.')
    if d:
        if len(d) == 3:
            if len(d[2]) < 4:  # je rok mensi nez 2000?
                date_string_iso = '19' + d[2] + '-' + d[1] + '-' + d[0]
            else:
                date_string_iso = d[2] + '-' + d[1] + '-' + d[0]
    return date_string_iso


def init_config():
    out = {}
    if os.path.isfile(CONFIG_FILE_PATH):
        with open(CONFIG_FILE_PATH, "r") as yamlfile:
            out = yaml.load(yamlfile, Loader=yaml.FullLoader)
            LOG.logger.info('Configuration loaded')
        return out
    out['jasu'] = JASU_CONFIG_DEFAULT
    out['data_source'] = DATA_SOURCE_DICTIONARY
    out['filenames'] = FILENAMES_DICTIONARY_DEAFULT
    out['elasticsearch'] = ES_CONFIG
    # out['log'] = LOG_CONFIG
    out['scheduler'] = CRON_MAP
    with open(CONFIG_FILE_PATH, 'w') as yamlfile:
        yaml.dump(out, yamlfile)
        LOG.logger.info('Configuration stored')
    return out


LOG = Log()
CONFIG = init_config()
FILENAMES_DICTIONARY = {v: k for k, v in CONFIG['filenames'].items()}

ES_HOST_DEAFULT = '{}://{}:{}/'.format(
    CONFIG['elasticsearch']['protocol'],
    CONFIG['elasticsearch']['hostname'],
    CONFIG['elasticsearch']['port'])
user = None
password = None
if 'user' in CONFIG['elasticsearch']:
    user = CONFIG['elasticsearch']['user']
if 'password' in CONFIG['elasticsearch']:
    password = CONFIG['elasticsearch']['password']
if (user is not None) and (password is not None):
    ES_HOST_DEAFULT = '{}://{}:{}@{}:{}/'.format(
        CONFIG['elasticsearch']['protocol'],
        user,
        password,
        CONFIG['elasticsearch']['hostname'],
        CONFIG['elasticsearch']['port'])
ES_HOST = os.getenv('ES_HOST', ES_HOST_DEAFULT)
# BUFFER_SIZE = CONFIG['exporter']['buffer']
# JASU_CONFIG = CONFIG['jasu']
INDEX_DICTIONARY = create_map_from_list(CONFIG['elasticsearch']['index'])
