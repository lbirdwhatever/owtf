"""
owtf.core
~~~~~~~~~

The core is the glue that holds the components together and allows some of them to
communicate with each other. Basically injects dependencies so that they can be used
across modules.
"""

import os
import sys
import signal
import socket
import logging
import multiprocessing

import tornado
import psutil

from owtf.utils.file import FileOperations, catch_io_errors
from owtf.utils.commands import OutputCleaner
from owtf.http import transaction_logger
from owtf.workers.service import *
from owtf.utils.strings import ConsoleFormatter, FileFormatter
from owtf.config.service import get_logs_dir
from owtf.plugins.service import show_plugin_list


logger = logging.getLogger(__name__)

class Core(object):
    def __init__(self):
        """Initialize a Core instance.

        :return: instance of :class:`owtf.core.Core`
        :rtype::class:`owtf.core.Core`
        """
        FileOperations.create_missing_dirs(get_logs_dir())
        self.create_temp_storage_dirs()
        self.enable_logging()

    def start(self, options):
        """Start OWTF.

        :params list options: Options from the CLI.

        """
        if self.initialise_framework(options):
            if not options['nowebui']:
                return self.run_server()
            else:
                return self.run_cli()

    def initialise_framework(self, options):
        """This function initializes the entire framework

        :param options: Additional arguments for the component initializer
        :type options: `dict`
        :return: True if all commands do not fail
        :rtype: `bool`
        """
        self.proxy_mode = options["proxy_mode"]
        logger.info("Loading framework please wait..")
        self.initialise_plugin_handler_and_params(options)
        # No processing required, just list available modules.
        if options['list_plugins']:
            show_plugin_list(options['list_plugins'])
            self.finish()
        command = self.get_command(options['argv'])

        self.start_proxy(options)  # Proxy mode is started in that function.
        # Set anonymized invoking command for error dump info.
        self.error_handler.set_command(OutputCleaner.anonymise_command(command))
        return True

    def initialise_plugin_handler_and_params(self, options):
        """Init step for plugin handler and params

        . note::
         The order is important here ;)

        :param options: Additional arguments
        :type options: `dict`
        :return:
        :rtype: None
        """
        # If OWTF is run without the Web UI, the WorkerManager should exit as soon as all jobs have been completed.
        # Otherwise, keep WorkerManager alive.
        self.worker_manager = worker.WorkerManager(keep_working=not options['nowebui'])

    def run_server(self):
        """This method starts the interface server"""
        self.server = server.APIServer()
        logger.warn("http://%s:%s <-- Web UI URL", get_val("SERVER_ADDR"), get_val("UI_SERVER_PORT"))
        logger.info("Press Ctrl+C when you spawned a shell ;)")
        self.disable_console_logging()
        self.interface_server.start()
        self.file_server = server.FileServer()
        self.file_server.start()

    def run_cli(self):
        """This method starts the CLI server."""
        self.cli_server = server.CliServer()
        self.cli_server.start()

    def finish(self):
        """Finish OWTF framework after freeing resources.

        :return: None
        :rtype: None

        """
        if getattr(self, "tor_process", None) is not None:
            self.tor_process.terminate()
        else:
            if getattr(self, "plugin_handler", None) is not None:
                self.plugin_handler.clean_up()
            if getattr(self, "proxy_process", None) is not None:
                logging.info("Stopping inbound proxy processes and cleaning up. Please wait!")
                self.proxy_process.clean_up()
                self.kill_children(self.proxy_process.pid)
                self.proxy_process.join()
            if getattr(self, "transaction_logger", None) is not None:
                # No signal is generated during closing process by terminate()
                self.transaction_logger.poison_q.put('done')
                self.transaction_logger.join()
            if getattr(self, "worker_manager", None) is not None:
                # Properly stop the workers.
                self.worker_manager.clean_up()
            if getattr(self, "db", None) is not None:
                # Properly stop any DB instances.
                self.db.clean_up()
            # Stop any tornado instance.
            if getattr(self, "cli_server", None) is not None:
                self.cli_server.clean_up()
            tornado.ioloop.IOLoop.instance().stop()
            sys.exit(0)
