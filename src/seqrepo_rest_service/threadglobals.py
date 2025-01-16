"""per-thread globals for seqrepo REST APIs"""

import datetime
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

def _convert_time(real_seconds, user_seconds):
    dt_real = datetime.timedelta(seconds = real_seconds)
    dt_user = datetime.timedelta(seconds = user_seconds)    
    return str(dt_real), str(dt_user)

def log_request(alias, start, end, time_real, time_user, sr):
    """
    We are seeing cpu spikes from the REST service even when we don't think there are any requests coming in. 
    This method will log requests so we can see if indeed there are requests associated with the increased cpu.  
    To prevent excessive logging log messages are limited to once every 30s.
    """
    # Minimum number of seconds between log messages
    log_request_interval = 60
    
    log_request_last_log_time = current_app.config["log_request_last_log_time"]
    number_of_seconds_since_last_query = time.time() - log_request_last_log_time

    if number_of_seconds_since_last_query >= log_request_interval:
        http_client_ip = request.remote_addr
        
        real_time, user_time = _convert_time(time_real, time_user)

        if hasattr(sr.sequences._open_for_reading, "cache_info"):
            cache_results = sr.sequences._open_for_reading.cache_info()
        else:
            cache_results = 'no fd cache'

        _logger.info(f"seqrepo rest request: {alias}, {start}, {end}, {http_client_ip}, {real_time}, {user_time}, {cache_results}")

        # This does not need to be threadsafe 
        current_app.config["log_request_last_log_time"] = time.time()
