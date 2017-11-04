"""
owtf.proxy.cli
~~~~~~~~~~~~~~
Command line interface for the MiTM proxy
"""

import logging

from owtf.config.service import *
from owtf.error_handler import ErrorHandler
import owtf.transaction.transaction_logger


def start_proxy(options):
    """ The proxy along with supporting processes are started here

    :param options: Optional arguments
    :type options: `dict`
    :return:
    :rtype: None
    """
    if True:
        # Check if port is in use
        try:
            temp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            temp_socket.bind((get('INBOUND_PROXY_IP'), int(get('INBOUND_PROXY_PORT'))))
            temp_socket.close()
        except socket.error:
            self.error_handler.abort_framework("Inbound proxy address %s:%s already in use" %
                (get('INBOUND_PROXY_IP'), get("INBOUND_PROXY_PORT")))
        # If everything is fine.
        proxy_process = proxy.ProxyProcess()
        proxy_process.initialize(
            options['OutboundProxy'], options['OutboundProxyAuth'])
        transaction_logger = transaction_logger.TransactionLogger(
            cache_dir=get('INBOUND_PROXY_CACHE_DIR'))
        logging.warn(
            "%s:%s <-- HTTP(S) Proxy to which requests can be directed",
            get('INBOUND_PROXY_IP'),
            get("INBOUND_PROXY_PORT"))
        proxy_process.start()
        logging.debug("Starting Transaction logger process")
        transaction_logger.start()
        logging.debug("Proxy transaction's log file at %s", get("PROXY_LOG"))
    else:
        ComponentInitialiser.initialisation_phase_3(
            options['OutboundProxy'])


if __name__ == "__main__":
    start_proxy(options)
