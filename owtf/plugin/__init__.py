from owtf.config.config import select_user_or_default_config_path, get_val
from owtf.shell.blocking_shell import shell_exec

from .service import load_test_groups, load_plugins
from .scanner import SCANS_FOLDER

load_test_groups((
    get_val("WEB_TEST_GROUPS"),
    get_val("WEB_PLUGIN_CONFIG_DIR")),
    "web"
)

load_test_groups(select_user_or_default_config_path(
    get_val("NET_TEST_GROUPS"),
    get_val("NET_PLUGIN_CONFIG_DIR")),
    "network"
)

load_test_groups(select_user_or_default_config_path(
    get_val("AUX_TEST_GROUPS"),
    get_val("AUX_PLUGIN_CONFIG_DIR")),
    "auxiliary"
)

# After loading the test groups then load the plugins, because of many-to-one relationship
load_plugins()
shell_exec("mkdir %s" % SCANS_FOLDER)
