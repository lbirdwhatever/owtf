"""
owtf.config.service
~~~~~~~~~~~~~~~~~~

The Configuration object parses all configuration files, loads them into
memory, derives some settings and provides framework modules with a central
repository to get info.
"""

import os
import re
import logging
import socket
from copy import deepcopy
try: #PY3
    from urllib.parse import urlparse
except ImportError:  #PY2
     from urlparse import urlparse
from collections import defaultdict
try:
    import configparser as parser
except ImportError:
    import ConfigParser as parser

from owtf.api.factory import db
from owtf.exceptions import InvalidConfigurationReference
from owtf.config import models
from owtf.exceptions import PluginAbortException, DBIntegrityException, UnresolvableTargetException
from owtf.managers import target as target_manager
from owtf.utils import is_internal_ip, directory_access, FileOperations


config_path = os.path.expanduser(os.path.join("~", '.owtf', 'conf', 'framework.cfg'))

profiles = {
    "GENERAL_PROFILE": None,
    "RESOURCES_PROFILE": None,
    "WEB_PLUGIN_ORDER_PROFILE": None,
    "NET_PLUGIN_ORDER_PROFILE": None,
    "MAPPING_PROFILE": None
}


def select_user_or_default_config_path(file_path, default_path=""):
    """If user config files are present return the passed file path, else the default config file path

    :param file_path: Path of config file to locate
    :param default_path: Default path of this file relative to "@@@root_dir@@@/configuration/" excluding filename
    :return: Absolute path of the file if found else default path
    """
    file_path = os.path.expanduser(file_path)
    if os.path.isfile(file_path):
        return file_path
    path = os.path.join(get_val("CONFIG_DIR"), default_path, os.path.basename(file_path))
    return path


def framework_config_file_path():
    """Returns the full path to the configuration file in ~/.owtf or fallback to package specific file

    :return: path of the existing configuration file
    :rtype: `str`
    """
    if os.path.isfile(config_path):
        return config_path
    path = os.path.join(root_dir, 'data', 'conf', os.path.basename(config_path))
    return path

def load_config_from_file(config_path):
    """Load the configuration into a global dictionary.

    :param config_path: The configuration file path
    :type config_path: `str`
    :return: None
    :rtype: None
    """
    logging.info("Loading config from: %s.." % config_path)
    config_file = FileOperations.open(config_path, 'r')
    set_val('FRAMEWORK_DIR', root_dir)  # Needed Later.
    for line in config_file:
        try:
            key = line.split(':')[0]
            if key[0] == '#':  # Ignore comment lines.
                continue
            value = line.replace("%s: " % key, "").strip()
            set_val(key,
                        multi_replace(value, {'FRAMEWORK_DIR': root_dir, 'OWTF_PID': str(owtf_pid)}))
        except ValueError:
            error_handler.abort_framework("Problem in config file: %s -> Cannot parse line: %s" % (
                config_path, line))


def load_config_db_file(file_path):
    """Load Db config from file

    :param file_path: The path to config file
    :type file_path: `str`
    :return: None
    :rtype: None
    """
    file_path = config.select_user_or_default_config_path(file_path)
    logging.info("Loading Configuration from: %s.." % file_path)
    config_parser = parser.RawConfigParser()
    # Otherwise all the keys are converted to lowercase xD
    config_parser.optionxform = str
    if not os.path.isfile(file_path):  # check if the config file exists
        error_handler.abort_framework(
            "Config file not found at: %s" % file_path)
    config_parser.read(file_path)
    for section in config_parser.sections():
        for key, value in config_parser.items(section):
            old_config_obj = db.session.query(models.ConfigSetting).get(key)
            if not old_config_obj or not old_config_obj.dirty:
                if not key.endswith("_DESCRIP"):  # _DESCRIP are help values
                    config_obj = models.ConfigSetting(
                        key=key, value=value, section=section)
                    # If _DESCRIP at the end, then use it as help text
                    if config_parser.has_option(section, "%s_DESCRIP" % key):
                        config_obj.descrip = config_parser.get(
                            section, "%s_DESCRIP" % key)
                    db.session.merge(config_obj)
    db.session.commit()


def get(key):
    """Get the value of the key from DB

    :param key: Key to lookup
    :type key: `str`
    :return: Value
    :rtype: `str`
    """
    obj = db.session.query(models.ConfigSetting).get(key)
    if obj:
        return config.multi_replace(obj.value, config.get_replacement_dict())
    else:
        return None


def derive_config_dict(config_obj):
    """Get the config dict from the obj

    :param config_obj: The config object
    :type config_obj:
    :return:
    :rtype:
    """
    if config_obj:
        config_dict = dict(config_obj.__dict__)
        config_dict.pop("_sa_instance_state")
        return config_dict
    else:
        return config_obj


def derive_config_dicts(config_obj_list):
    """Derive multiple config dicts

    :param config_obj_list: List of all config objects
    :type config_obj_list: `list`
    :return: List of config dicts
    :rtype: `list`
    """
    config_dict_list = []
    for config_obj in config_obj_list:
        if config_obj:
            config_dict_list.append(derive_config_dict(config_obj))
    return config_dict_list


def gen_query(criteria):
    """Generate query

    :param criteria: Filter criteria
    :type criteria: `dict`
    :return:
    :rtype:
    """
    query = db.session.query(models.ConfigSetting)
    if criteria.get("key", None):
        if isinstance(criteria["key"], str):
            query = query.filter_by(key=criteria["key"])
        if isinstance(criteria["key"], list):
            query = query.filter(models.ConfigSetting.key.in_(criteria["key"]))
    if criteria.get("section", None):
        if isinstance(criteria["section"], str):
            query = query.filter_by(section=criteria["section"])
        if isinstance(criteria["section"], list):
            query = query.filter(
                models.ConfigSetting.section.in_(criteria["section"]))
    if criteria.get('dirty', None):
        if isinstance(criteria.get('dirty'), list):
            criteria['dirty'] = criteria['dirty'][0]
        query = query.filter_by(
            dirty=config.ConvertStrToBool(criteria['dirty']))
    return query.order_by(models.ConfigSetting.key)


def get_all(criteria=None):
    """Get all config dicts for a criteria

    :param criteria: Filter criteria
    :type criteria: `str`
    :return: Config dict
    :rtype: `dict`
    """
    if not criteria:
        criteria = {}
    query = gen_query(criteria)
    return derive_config_dicts(query.all())


def get_all_tools(self):
    """Get all tools from the config DB

    :return: Config dict for all tools
    :rtype: `dict`
    """
    results = db.session.query(models.ConfigSetting).filter(
        models.ConfigSetting.key.like("%TOOL_%")).all()
    config_dicts = derive_config_dicts(results)
    for config_dict in config_dicts:
        config_dict["value"] = config.multi_replace(
            config_dict["value"], config.get_replacement_dict())
    return config_dicts


def get_sections(self):
    """Get all sections in from the config db

    :return: List of sections
    :rtype: `list`
    """
    sections = db.session.query(models.ConfigSetting.section).distinct().all()
    sections = [i[0] for i in sections]
    return sections


def update(key, value):
    """Update the configuration value for a key

    :param key: Key whose value to update
    :type key: `str`
    :param value: New value
    :type value: `str`
    :return: None
    :rtype: None
    """
    config_obj = db.session.query(models.ConfigSetting).get(key)
    if config_obj:
        config_obj.value = value
        config_obj.dirty = True
        db.session.merge(config_obj)
        db.session.commit()
    else:
        raise InvalidConfigurationReference(
            "No setting exists with key: %s" % str(key))


def get_replacement_dict(self):
    """Get the config dict

    :return: Replaced dict
    :rtype: `dict`
    """
    config_dict = {}
    config_list = db.session.query(
        models.ConfigSetting.key, models.ConfigSetting.value).all()
    for key, value in config_list:  # Need a dict
        config_dict[key] = value
    return config_dict


def get_tcp_ports(startport, endport):
    """Get TCP ports from the config file

    :param startport: Start port in a range
    :type startport: `str`
    :param endport: Endport
    :type endport: `str`
    :return: Comma-separate string of tcp ports
    :rtype: `str`
    """
    return ','.join(get("TCP_PORTS").split(',')[int(startport):int(endport)])


def get_udp_ports(startport, endport):
    """Get UDP ports from the config file

    :param startport: Start port in a range
    :type startport: `str`
    :param endport: Endport
    :type endport: `str`
    :return: Comma-separate string of udp ports
    :rtype: `str`
    """
    return ','.join(get("UDP_PORTS").split(',')[int(startport):int(endport)])


def load_works(target_urls, options):
    """Select the proper plugins to run against the target URLs.

    :param list target_urls: the target URLs
    :param dict options: the options from the CLI.

    """
    for target_url in target_urls:
        if target_url:
            load_work(target_url, options)


def load_work(target_url, options):
    """Select the proper plugins to run against the target URL.

    .. note::

        If plugin group is not specified and several targets are fed, OWTF
        will run the WEB plugins for targets that are URLs and the NET
        plugins for the ones that are IP addresses.

    :param str target_url: the target URL
    :param dict options: the options from the CLI.
    """
    target = target.get_target_config_dicts({'target_url': target_url})
    group = options['PluginGroup']
    if options['OnlyPlugins'] is None:
        # If the plugin group option is the default one (not specified by the user).
        if group is None:
            group = 'web'  # Default to web plugins.
            # Run net plugins if target does not start with http (see #375).
            if not target_url.startswith(('http://', 'https://')):
                group = 'network'
        filter_data = {'type': options['PluginType'], 'group': group}
    else:
        filter_data = {"code": options.get("OnlyPlugins"), "type": options.get("PluginType")}
    plugins = db_plugin.get_all(filter_data)
    if not plugins:
        logging.error("No plugin found matching type '%s' and group '%s' for target '%s'!" %
                        (options['PluginType'], group, target))
    worklist_manager.add_work(target, plugins, force_overwrite=options["Force_Overwrite"])


def load_targets(options):
    """Load targets into the DB

    :param options: User supplied arguments
    :type options: `dict`
    :return: Added targets
    :rtype: `list`
    """
    scope = options['Scope']
    if options['PluginGroup'] == 'auxiliary':
        scope = get_aux_target(options)
    added_targets = []
    for target in scope:
        try:
            target.add_target(target)
            added_targets.append(target)
        except DBIntegrityException:
            logging.warning("%s already exists in DB" % target)
            added_targets.append(target)
        except UnresolvableTargetException as e:
            logging.error("%s" % e.parameter)
    return added_targets


def get_aux_target(options):
    """This function returns the target for auxiliary plugins from the parameters provided

    :param options: User supplied arguments
    :type options: `dict`
    :return: List of targets for aux plugins
    :rtype: `list`
    """
    # targets can be given by different params depending on the aux plugin we are running
    # so "target_params" is a list of possible parameters by which user can give target
    target_params = ['RHOST', 'TARGET', 'SMB_HOST', 'BASE_URL', 'SMTP_HOST']
    plugin_params = get_component("plugin_params")
    targets = None
    if plugin_params.process_args():
        for param in target_params:
            if param in plugin_params.Args:
                targets = plugin_params.Args[param]
                break  # it will capture only the first one matched
        repeat_delim = ','
        if targets is None:
            logging.error("Aux target not found! See your plugin accepted parameters in ./plugins/ folder")
            return []
        if 'REPEAT_DELIM' in plugin_params.Args:
            repeat_delim = plugin_params.Args['REPEAT_DELIM']
        return targets.split(repeat_delim)
    else:
        return []


def load_proxy_config(options):
    """Load proxy related configuration

    :param options: User supplied arguments
    :type options: `dict`
    :return: None
    :rtype: None
    """
    if options['InboundProxy']:
        if len(options['InboundProxy']) == 1:
            options['InboundProxy'] = [get_val('INBOUND_PROXY_IP'), options['InboundProxy'][0]]
    else:
        options['InboundProxy'] = [get_val('INBOUND_PROXY_IP'), get_val('INBOUND_PROXY_PORT')]
    set_val('INBOUND_PROXY_IP', options['InboundProxy'][0])
    set_val('INBOUND_PROXY_PORT', options['InboundProxy'][1])
    set_val('INBOUND_PROXY', ':'.join(options['InboundProxy']))
    set_val('PROXY', ':'.join(options['InboundProxy']))


def get_resources(resource_type):
    """Replace the resources placeholders with the relevant config.

    :param resource_type: Type of resource to get
    :type resource_type: `str`
    :return: Fetched resource
    :rtype: `str`
    """
    return resource.get_resources(resource_type)


def get_resource_list(resource_type_list):
    """Fetch the resource list

    :param resource_type_list: Type of resource list
    :type resource_type_list: `str`
    :return: Resource list
    :rtype: `list`
    """
    return resource.get_resource_list(resource_type_list)


def get_raw_resources(resource_type):
    """Fetch the raw resource

    :param resource_type_list: Type of resource list
    :type resource_type_list: `str`
    :return: Resource
    :rtype: `str`
    """
    return resource[resource_type]


def derive_config_from_url(target_URL):
    """Automatically find target information based on target name.

    .note::
        If target does not start with 'http' or 'https', then it is considered as a network target.

        + target host
        + target port
        + target url
        + target path
        + etc.

    :param target_URL: Target url supplied
    :type target_URL: `str`
    :return: Target config dictionary
    :rtype: `dict`
    """
    target_config = dict(target_manager.TARGET_CONFIG)
    target_config['target_url'] = target_URL
    try:
        parsed_url = urlparse(target_URL)
        if not parsed_url.hostname and not parsed_url.path:  # No hostname and no path, urlparse failed.
            raise ValueError
    except ValueError:  # Occurs sometimes when parsing invalid IPv6 host for instance
        raise UnresolvableTargetException("Invalid hostname '%s'" % str(target_URL))

    host = parsed_url.hostname
    if not host:  # Happens when target is an IP (e.g. 127.0.0.1)
        host = parsed_url.path  # Use the path as host (e.g. 127.0.0.1 => host = '' and path = '127.0.0.1')
        host_path = host
    else:
        host_path = parsed_url.hostname + parsed_url.path

    url_scheme = parsed_url.scheme
    protocol = parsed_url.scheme
    if parsed_url.port is None:  # Port is blank: Derive from scheme (default port set to 80).
        try:
            host, port = host.rsplit(':')
        except ValueError:  # Raised when target doesn't contain the port (e.g. google.fr)
            port = '80'
            if 'https' == url_scheme:
                port = '443'
    else:  # Port found by urlparse.
        port = str(parsed_url.port)

    # Needed for google resource search.
    target_config['host_path'] = host_path
    # Some tools need this!
    target_config['url_scheme'] = url_scheme
    # Some tools need this!
    target_config['port_number'] = port
    # Set the top URL.
    target_config['host_name'] = host

    host_ip = get_ip_from_hostname(host)
    host_ips = get_ips_from_hostname(host)
    target_config['host_ip'] = host_ip
    target_config['alternative_ips'] = host_ips

    ip_url = target_config['target_url'].replace(host, host_ip)
    target_config['ip_url'] = ip_url
    target_config['top_domain'] = target_config['host_name']

    hostname_chunks = target_config['host_name'].split('.')
    if target_config['target_url'].startswith(('http', 'https')):  # target considered as hostname (web plugins)
        if not target_config['host_name'] in target_config['alternative_ips']:
            target_config['top_domain'] = '.'.join(hostname_chunks[1:])
        # Set the top URL (get "example.com" from "www.example.com").
        target_config['top_url'] = "%s://%s:%s" % (protocol, host, port)
    else:  # target considered as IP (net plugins)
        target_config['top_domain'] = ''
        target_config['top_url'] = ''
    return target_config


def is_set(key):
    """Checks if the key is set in the config dict

    :param key: Key to check
    :type key: `str`
    :return: True if present, else False
    :rtype: `bool`
    """
    key = pad_key(key)
    config = get_config_dict()
    for type in CONFIG_TYPES:
        if key in config[type]:
            return True
    return False


def get_key_val(key):
    """Gets the right config for target / general.

    :param key: The key
    :type key: `str`
    :return: Value for the key
    """
    config = get_config_dict()
    for type in CONFIG_TYPES:
        if key in config[type]:
            return config[type][key]


def get_val(key):
    """Transparently gets config info from target or General.

    :param key: Key
    :type key: `str`
    :return: The value for the key
    """
    try:
        key = pad_key(key)
        return get_key_val(key)
    except KeyError:
        message = "The configuration item: %s does not exist!" % key
        error_handler.add(message)
        # Raise plugin-level exception to move on to next plugin.
        raise PluginAbortException(message)


def get_logs_dir():
    """
    Get log directory by checking if abs or relative path is provided in
    config file
    """
    logs_dir = get_val("LOGS_DIR")
    # Check access for logs dir parent directory because logs dir may not be created.
    if os.path.isabs(logs_dir) and directory_access(os.path.dirname(logs_dir), "w+"):
        return logs_dir
    else:
        return os.path.join(get_output_dir(), logs_dir)


def get_log_path(process_name):
    """Get the log file path based on the process name

    :param process_name: Process name
    :type process_name: `str`
    :return: Path to the specific log file
    :rtype: `str`
    """
    log_file_name = "%s.log" % process_name
    return os.path.join(get_logs_dir(), log_file_name)


def set_general_val(type, key, value):
    """ Set value for a key in any config file

    :param type: Type of config file, framework or general.cfg
    :type type: `str`
    :param key: The key
    :type key: `str`
    :param value: Value to be set
    :type value:
    :return: None
    :rtype: None
    """
    config[type][key] = value


def set_val(key, value):
    """set config items in target-specific or General config."""
    # Store config in "replacement mode", that way we can multiple-replace
    # the config on resources, etc.
    key = REPLACEMENT_DELIMITER + key + REPLACEMENT_DELIMITER
    type = 'other'
    # Only when value is a string, store in replacements config.
    if isinstance(value, str):
        type = 'string'
    return set_general_val(type, key, value)


def get_framework_config_dict():
    return get_config_dict()['string']


def get_replacement_dict():
    """Returns a dictionary with framework directory path

    :return:
    :rtype:
    """
    return {"FRAMEWORK_DIR": root_dir}


def get_config_dict():
    """Get the global config dictionary

    :return: None
    :rtype: None
    """
    return config


def show():
    """Print all keys and values from configuration dictionary

    :return: None
    :rtype: None
    """
    logging.info("Configuration settings: ")
    for k, v in list(get_config_dict().items()):
        logging.info("%s => %s" % (str(k), str(v)))


def get_output_dir():
    """Gets the output directory for the session

    :return: The path to the output directory
    :rtype: `str`
    """
    output_dir = os.path.expanduser(get_val("OUTPUT_PATH"))
    if not os.path.isabs(output_dir) and directory_access(os.getcwd(), "w+"):
        return output_dir
    else:
        # The output_dir may not be created yet, so check its parent.
        if directory_access(os.path.dirname(output_dir), "w+"):
            return output_dir
    return os.path.expanduser(os.path.join(get_val("SETTINGS_DIR"), output_dir))


def get_output_dir_target():
    """Returns the output directory for the targets

    :return: Path to output directory
    :rtype: `str`
    """
    return os.path.join(get_output_dir(), get_val("TARGETS_DIR"))


def get_dir_worker_logs():
    """Returns the output directory for the worker logs

    :return: Path to output directory for the worker logs
    :rtype: `str`
    """
    return os.path.join(get_output_dir(), get_val("WORKER_LOG_DIR"))


def cleanup_target_dirs(target_url):
    """Cleanup the directories for the specific target

    :return: None
    :rtype: None
    """
    return FileOperations.rm_tree(get_target_dir(target_url))


def get_target_dir(target_url):
    """Gets the specific directory for a target in the target output directory

    :param target_url: Target URL for which directory path is needed
    :type target_url: `str`
    :return: Path to the target URL specific directory
    :rtype: `str`
    """
    clean_target_url = target_url.replace("/", "_").replace(":", "").replace("#", "")
    return os.path.join(get_output_dir_target(), clean_target_url)


def create_output_dir_target(target_url):
    """Creates output directories for the target URL

    :param target_url: The target URL
    :type target_url: `str`
    :return: None
    :rtype: None
    """
    FileOperations.create_missing_dirs(get_target_dir(target_url))
