import os
import sys

HOME_DIR = os.path.expanduser("~")
SETTINGS_DIR = os.path.join(HOME_DIR, ".owtf")
FRAMEWORK_DIR = os.path.abspath(os.path.dirname(__file__))
DEFAULT_CONFIG_DIR = os.path.join(FRAMEWORK_DIR, "conf")
DB_CONFIG = os.path.join(SETTINGS_DIR, 'db.cfg')
PLUGINS_DIR = os.path.join(SETTINGS_DIR, "plugins")

WEB_TEST_GROUPS = os.path.join(SETTINGS_DIR, "profiles", "web_groups.yaml")
NET_TEST_GROUPS = os.path.join(SETTINGS_DIR, "profiles", "net_groups.yaml")
AUX_TEST_GROUPS = os.path.join(SETTINGS_DIR, "profiles", "aux_groups.yaml")

DEFAULT_GENERAL_PROFILE = os.path.join(SETTINGS_DIR, "conf", "general.yaml")
DEFAULT_RESOURCES_PROFILE = os.path.join(SETTINGS_DIR, "conf", "resources.cfg")
DEFAULT_MAPPING_PROFILE = os.path.join(SETTINGS_DIR, "conf", "mappings.yaml")

API_SERVER_ADDR = 127.0.0.1
API_SERVER_PORT = 8009
FILE_SERVER_PORT = 8010
ZAP_PROXY_ADDR = 127.0.0.1
ZAP_PROXY_PORT = 8090

# Relative paths
OUTPUT_PATH =  owtf_review
AUX_OUTPUT_PATH = owtf_review/auxiliary
TARGETS_DIR = targets
WORKER_LOG_DIR = logs
