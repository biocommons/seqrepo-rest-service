"""per-thread globals for seqrepo REST APIs"""

import logging
import time

from biocommons.seqrepo import SeqRepo
from connexion import request
from flask import current_app

_logger = logging.getLogger(__name__)


def get_seqrepo():
    seqrepo_dir = current_app.config["seqrepo_dir"]
    if _get_or_create("seqrepo", None, False) is None:
        _logger.info("Opening seqrepo_dir=%s", seqrepo_dir)
    return _get_or_create("seqrepo", lambda: SeqRepo(root_dir=seqrepo_dir))


def _get_or_create(k, f, create=True):
    k = "_" + k
    o = getattr(_get_or_create, k, None)
    if o is None and create:
        o = f()
        setattr(_get_or_create, k, o)
    return o

def log_request(alias, start, end):
    """
    We are seeing cpu spikes from the REST service even when we don't think there are any requests coming in. 
    This method will log requests so we can see if indeed there are requests associated with the increased cpu.  
    To prevent excessive logging log messages are limited to once every 30s.
    """
    # Minimum number of seconds between log messages
    log_request_interval = 30
    
    http_client_ip = request.remote_addr
    
    log_request_last_log_time = current_app.config["log_request_last_log_time"]
    number_of_seconds_since_last_query = time.time() - log_request_last_log_time

    if number_of_seconds_since_last_query >= log_request_interval:
        _logger.info(f"seqrepo rest request: alias={alias}, start={start}, end={end}, http_client_ip={http_client_ip}")
            
    # This does not need to be threadsafe 
    current_app.config["log_request_last_log_time"] = time.time()
    