"""
owtf.cli

This is the command-line front-end in charge of processing arguments and call the framework.
"""

from __future__ import print_function

import os
import sys
import logging

from owtf.core import Core
from owtf.lib.cli_options import usage, parse_options
from owtf.plugins.service import get_groups_for_plugins, get_all_plugin_groups, get_all_plugin_types
from owtf import __version__, __release__


def banner():
    """Prints a figlet type banner"""

    print("""\033[92m
 _____ _ _ _ _____ _____
|     | | | |_   _|   __|
|  |  | | | | | | |   __|
|_____|_____| |_| |__|

        @owtfp
    http://owtf.org
    \033[0m""")


def get_plugins_from_arg(arg):
    """ Returns a list of requested plugins and plugin groups

    :param arg: Comma separated list of plugins
    :type arg: `str`
    :return: List of plugins and plugin groups
    :rtype: `list`
    """
    plugins = arg.split(',')
    plugin_groups = get_groups_for_plugins(plugins)
    if len(plugin_groups) > 1:
        usage("The plugins specified belong to several plugin groups: '%s'" % str(plugin_groups))
    return [plugins, plugin_groups]


def process_options(user_args):
    """ The main argument processing function

    :param user_args: User supplied arguments
    :type user_args: `str`
    :return: A dictionary of arguments
    :rtype: `dict`
    """
    try:
        valid_groups = get_all_plugin_groups()
        valid_types = get_all_plugin_types() + ['all', 'quiet']
        arg = parse_options(user_args, valid_groups, valid_types)
    except KeyboardInterrupt as e:
        usage("Invalid OWTF option(s) %s" % e)
        sys.exit(0)

    # Default settings:
    profiles = {}
    plugin_group = arg.plugin_group

    if arg.only_plugins:
        arg.only_plugins, plugin_groups = get_plugins_from_arg(arg.only_plugins)
        try:
            # Set Plugin Group according to plugin list specified
            plugin_group = plugin_groups[0]
        except IndexError:
            usage("Please use either OWASP/OWTF codes or Plugin names")
        logging.info("Defaulting Plugin Group to '%s' based on list of plugins supplied" % plugin_group)

    if arg.except_plugins:
        arg.except_plugins, plugin_groups = get_plugins_from_arg(arg.except_plugins)

    if arg.outbound_proxy:
        arg.outbound_proxy = arg.outbound_proxy.split('://')
        if len(arg.outbound_proxy) == 2:
            arg.outbound_proxy = arg.outbound_proxy + arg.outbound_proxy.pop().split(':')
            if arg.outbound_proxy[0] not in ["socks", "http"]:
                usage("Invalid argument for outbound proxy")
        else:
            arg.outbound_proxy = arg.outbound_proxy.pop().split(':')
        # OutboundProxy should be type://ip:port
        if len(arg.outbound_proxy) not in [2, 3]:
            usage("Invalid argument for outbound proxy")
        else:  # Check if the port is an int.
            try:
                int(arg.outbound_proxy[-1])
            except ValueError:
                usage("Invalid port provided for outbound proxy")

    if arg.inbound_proxy:
        arg.inbound_proxy = arg.inbound_proxy.split(':')
        # InboundProxy should be (ip:)port:
        if len(arg.inbound_proxy) not in [1, 2]:
            usage("Invalid argument for inbound proxy")
        else:
            try:
                int(arg.inbound_proxy[-1])
            except ValueError:
                usage("Invalid port for inbound proxy")

    plugin_types_for_group = get_types_for_plugin_group(plugin_group)
    if arg.plugin_type == 'all':
        arg.plugin_type = plugin_types_for_group
    elif arg.plugin_type == 'quiet':
        arg.plugin_type = ['passive', 'semi_passive']

    scope = arg.targets or []  # Arguments at the end are the URL target(s)
    num_targets = len(scope)
    if plugin_group != 'auxiliary' and num_targets == 0 and not arg.list_plugins:
        pass
    elif num_targets == 1:  # Check if this is a file
        if os.path.isfile(scope[0]):
            logging.info("Scope file: trying to load targets from it ..")
            new_scope = []
            for target in open(scope[0]).read().split("\n"):
                clean_target = target.strip()
                if not clean_target:
                    continue  # Skip blank lines
                new_scope.append(clean_target)
            if len(new_scope) == 0:  # Bad file
                usage("Please provide a scope file (1 target x line)")
            scope = new_scope

    for target in scope:
        if target[0] == "-":
            usage("Invalid Target: " + target)

    args = ''
    if plugin_group == 'auxiliary':
        # For auxiliary plugins, the scope are the parameters.
        args = scope
        # auxiliary plugins do not have targets, they have metasploit-like parameters.
        scope = ['auxiliary']

    return {
        'list_plugins': arg.list_plugins,
        'force_overwrite': arg.force_overwrite,
        'interactive': arg.interactive == 'yes',
        'simulation': arg.simulation,
        'scope': scope,
        'argv': sys.argv,
        'plugin_type': arg.plugin_type,
        'only_plugins': arg.only_plugins,
        'except_plugins': arg.except_plugins,
        'inbound_proxy': arg.inbound_proxy,
        'outbound_proxy': arg.outbound_proxy,
        'outbound_proxy_auth': arg.outbound_proxy_auth,
        'profiles': profiles,
        'plugin_group': plugin_group,
        'rport': arg.rport,
        'port_waves': arg.port_waves,
        'proxy_mode': arg.proxy_mode,
        'tor_mode': arg.tor_mode,
        'botnet_mode': arg.botnet_mode,
        'nowebui': arg.nowebui,
        'args': args
    }


def main(args):
    """ The main wrapper which loads everything

    :param args: User supplied arguments dictionary
    :type args: `dict`
    :return:
    :rtype: None
    """
    banner()
    # Get tool path from script path:
    root_dir = os.path.dirname(os.path.abspath(args[0])) or '.'
    owtf_pid = os.getpid()
    args = process_options(args[1:])

    # Initialise Framework.
    core = Core()
    logging.warn("OWTF Version: %s, Release: %s " % (__version__, __release__))
    try:
        if core.start(args):
            # Only if start is for real (i.e. not just listing plugins, etc)
            core.finish()  # Not Interrupted or Crashed.
    except KeyboardInterrupt:
        # NOTE: The user chose to interact: interactivity check redundant here:
        logging.warning("[-] OWTF was aborted by the user:")
        logging.info("[-] Please check report/plugin output files for partial results")
        # Interrupted. Must save the DB to disk, finish report, etc.
        core.finish()
    except SystemExit:
        pass  # Report already saved, framework tries to exit.
    finally:  # Needed to rename the temp storage dirs to avoid confusion.
        core.clean_temp_storage_dirs()
