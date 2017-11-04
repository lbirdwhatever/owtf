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

from owtf.dependency_management.dependency_resolver import BaseComponent
from owtf.dependency_management.component_initialiser import ComponentInitialiser
from owtf.utils import FileOperations, catch_io_errors, OutputCleaner
from owtf.api import server
from owtf.proxy import proxy, transaction_logger
from owtf.managers import worker
from owtf.lib.formatters import ConsoleFormatter, FileFormatter


class Core(BaseComponent):

    """Main entry point for OWTF that manages the OWTF components."""

    COMPONENT_NAME = "core"

    def __init__(self):
        """Initialize a Core instance.

        .. note::

            [*] Tightly coupled, cohesive framework components
            [*] Order is important

            + IO decorated so as to abort on any permission errors
            + Required folders created
            + All other components are attached to core: shell, db etc... (using ServiceLocator)

        :return: instance of :class:`owtf.core.Core`
        :rtype::class:`owtf.core.Core`

        """
        self.register_in_service_locator()
        # ------------------------ IO decoration ------------------------ #
        # -------------------- Component attachment -------------------- #
        self.db = self.get_component("db")
        self.config = self.get_component("config")
        self.db_config = self.get_component("db_config")
        self.error_handler = self.get_component("error_handler")
        # ----------------------- Directory creation ----------------------- #
        FileOperations.create_missing_dirs(self.config.get_logs_dir())
        self.create_temp_storage_dirs()
        self.enable_logging()
        # The following attributes will be initialised later
        self.tor_process = None

    def create_temp_storage_dirs(self):
        """Create a temporary directory in /tmp with pid suffix.

        :return:
        :rtype: None
        """
        tmp_dir = os.path.join('/tmp', 'owtf')
        if not os.path.exists(tmp_dir):
            tmp_dir = os.path.join(tmp_dir, str(self.config.owtf_pid))
            if not os.path.exists(tmp_dir):
                FileOperations.make_dirs(tmp_dir)

    def clean_temp_storage_dirs(self):
        """Rename older temporary directory to avoid any further confusions.

        :return:
        :rtype: None
        """
        curr_tmp_dir = os.path.join('/tmp', 'owtf', str(self.config.owtf_pid))
        new_tmp_dir = os.path.join('/tmp', 'owtf', 'old-%d' % self.config.owtf_pid)
        if os.path.exists(curr_tmp_dir) and os.access(curr_tmp_dir, os.W_OK):
            os.rename(curr_tmp_dir, new_tmp_dir)


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
        self.proxy_mode = options["ProxyMode"]
        logging.info("Loading framework please wait..")
        ComponentInitialiser.initialisation_phase_3(options)
        self.initialise_plugin_handler_and_params(options)
        # No processing required, just list available modules.
        if options['list_plugins']:
            self.plugin_handler.show_plugin_list(options['list_plugins'])
            self.finish()
        self.config.process_phase2(options)
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

        self.plugin_handler = self.get_component("plugin_handler")
        self.plugin_params = self.get_component("plugin_params")
        # If OWTF is run without the Web UI, the WorkerManager should exit as soon as all jobs have been completed.
        # Otherwise, keep WorkerManager alive.
        self.worker_manager = worker.WorkerManager(keep_working=not options['nowebui'])

    def run_server(self):
        """This method starts the interface server"""
        self.interface_server = server.APIServer()
        logging.warn(
            "http://%s:%s <-- Web UI URL",
            self.config.get_val("SERVER_ADDR"),
            self.config.get_val("UI_SERVER_PORT"))
        logging.info("Press Ctrl+C when you spawned a shell ;)")
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

    def kill_children(self, parent_pid, sig=signal.SIGINT):
        """Kill all OWTF child process when the SIGINT is received

        :param parent_pid: The pid of the parent OWTF process
        :type parent_pid: `int`
        :param sig: Signal received
        :type sig: `int`
        :return:
        :rtype: None
        """
        def on_terminate(proc):
            """Log debug info on child process termination
            
            :param proc: Process pid
            :rtype: None
            """
            logging.debug("Process {} terminated with exit code {}".format(proc, proc.returncode))

        parent = psutil.Process(parent_pid)
        children = parent.children(recursive=True)
        for child in children:
            child.send_signal(sig)

        _, alive = psutil.wait_procs(children, callback=on_terminate)
        if not alive:
            # send SIGKILL
            for pid in alive:
                logging.debug("Process {} survived SIGTERM; trying SIGKILL" % pid)
                pid.kill()
        _, alive = psutil.wait_procs(alive, callback=on_terminate)
        if not alive:
            # give up
            for pid in alive:
                logging.debug("Process {} survived SIGKILL; giving up" % pid)
